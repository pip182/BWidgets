import asyncio
import ipaddress
from pathlib import Path
from datetime import datetime, timedelta
from ping3 import ping
from scapy.all import ARP, Ether, srp
from socket import gethostbyaddr
import requests
import json
import os


class NetworkScanner:
    def __init__(self, subnet, data_dir="data", vendor_url=None, verbose=False):
        """
        Initializes the NetworkScanner class.
        Args:
            subnet (str): CIDR notation of the network to scan (e.g., "192.168.1.0/24").
            data_dir (str): Directory to store data files.
            vendor_url (str): URL to fetch the MAC Vendor database.
            verbose (bool): Whether to enable verbose output.
        """
        self.subnet = subnet
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.vendor_file = self.data_dir / "mac_vendor_list.json"
        self.vendor_url = vendor_url or "https://maclookup.app/downloads/json-database/get-db"
        self.mac_vendor_list = self.load_mac_vendor_list()
        self.verbose = verbose

    def __call__(self):
        """
        Makes the class callable to execute a network scan directly.
        """
        return asyncio.run(self.scan_network())

    def log(self, message):
        """Logs a message if verbose mode is enabled."""
        if self.verbose:
            print(message)

    def update_mac_vendor_list(self):
        """Fetches and updates the MAC Vendor database."""
        try:
            self.log("Fetching MAC vendor list...")
            response = requests.get(self.vendor_url)
            response.raise_for_status()
            with open(self.vendor_file, "w") as file:
                json.dump(response.json(), file, indent=4)
            self.log(f"MAC vendor list updated successfully at {self.vendor_file}.")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching MAC vendor list: {e}")

    def is_file_older_than(self, filepath, days):
        """Checks if a file is older than a given number of days."""
        if not filepath.exists():
            return True
        return datetime.now() - datetime.fromtimestamp(filepath.stat().st_mtime) > timedelta(days=days)

    def load_mac_vendor_list(self):
        """Loads the MAC Vendor database from the local JSON file."""
        if self.is_file_older_than(self.vendor_file, 60):
            self.log("MAC vendor list is outdated or missing. Fetching a new list...")
            self.update_mac_vendor_list()

        try:
            with open(self.vendor_file, "r") as file:
                return json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def get_vendor_by_mac(self, mac):
        """Identifies the vendor for a given MAC address."""
        if not mac:
            return "Unknown"
        mac_prefix = mac[:8].upper()
        for entry in self.mac_vendor_list:
            if entry.get("macPrefix", "").upper() == mac_prefix:
                return entry.get("vendorName", "Unknown")
        return "Unknown"

    def ping3_ping(self, ip, timeout=1):
        """Sends an ICMP echo request using ping3."""
        try:
            latency = ping(ip, timeout=timeout)
            return round(latency * 1000) if latency else None
        except Exception:
            return None

    async def ping_device(self, ip):
        """Pings a device to check if it's online and measures latency."""
        latency = await asyncio.to_thread(self.ping3_ping, ip)
        self.log(f"Pinged {ip}: {'Online' if latency else 'Offline'}")
        return ip, latency

    async def get_mac_address(self, ip):
        """Retrieves the MAC address of a device using ARP packets."""
        try:
            arp_request = ARP(pdst=ip)
            broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
            answered_list = srp(broadcast / arp_request, timeout=2, verbose=False)[0]
            for _, received in answered_list:
                return received.hwsrc
        except Exception:
            return "Unknown"

    async def get_netbios_name(self, ip):
        """Queries the NetBIOS name of a device."""
        try:
            return gethostbyaddr(ip)[0]
        except Exception:
            return "Unknown"

    async def scan_device(self, ip):
        """Scans a single device for latency, MAC address, and NetBIOS name."""
        latency = await self.ping_device(ip)
        if latency[1] is not None:
            mac = await self.get_mac_address(ip)
            netbios_name = await self.get_netbios_name(ip)
            result = {
                "ip": ip,
                "mac": mac,
                "vendor": self.get_vendor_by_mac(mac),
                "netbios": netbios_name,
                "latency": latency[1],
            }
            self.log(f"Device found: {result}")
            return result
        return None

    async def scan_network(self):
        """Scans the network for active devices asynchronously."""
        self.log(f"Starting network scan for {self.subnet}...")
        network = ipaddress.IPv4Network(self.subnet, strict=False)
        tasks = [self.scan_device(str(ip)) for ip in network.hosts()]
        devices = await asyncio.gather(*tasks)
        return [device for device in devices if device]


if __name__ == "__main__":
    subnet = "192.168.1.0/24"
    scanner = NetworkScanner(subnet, verbose=True)
    devices = scanner()
    print("Devices found:", devices)
