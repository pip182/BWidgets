import asyncio
import ipaddress
import requests
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from socket import gethostbyaddr
from ping3 import ping  # Ensure this is installed: pip install ping3
from scapy.all import ARP, Ether, srp


class NetworkScanner:
    def __init__(self, subnet, data_dir="data", vendor_url=None):
        """
        Initializes the NetworkScanner class.

        Args:
            subnet (str): CIDR notation of the network to scan (e.g., "192.168.1.0/24").
            data_dir (str): Directory to store data files.
            vendor_url (str): URL to fetch the MAC Vendor database.
        """
        self.subnet = subnet
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.vendor_file = self.data_dir / "mac_vendor_list.json"
        self.vendor_url = vendor_url or "https://maclookup.app/downloads/json-database/get-db?t=24-12-12&h=c0dab9c1c637e9e1e0d5be186f4ab3df0cf069b3"
        self.mac_vendor_list = self.load_mac_vendor_list()

    def update_mac_vendor_list(self):
        """
        Fetches and updates the MAC Vendor database from the provided URL.
        Saves the database to a local JSON file.
        """
        try:
            print("Fetching MAC vendor list...")
            response = requests.get(self.vendor_url)
            response.raise_for_status()
            json_data = response.json()
            with open(self.vendor_file, "w") as file:
                json.dump(json_data, file, indent=4)
            print(f"MAC vendor list updated successfully at {self.vendor_file}.")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching MAC vendor list: {e}")
        except json.JSONDecodeError as e:
            print(f"Error decoding MAC vendor list: {e}")

    def is_file_older_than(self, filepath, days):
        """
        Checks if a file is older than a given number of days.

        Args:
            filepath (Path): The path to the file.
            days (int): The number of days to compare.

        Returns:
            bool: True if the file is older than the specified number of days, False otherwise.
        """
        if not filepath.exists():
            return True  # File doesn't exist; treat as outdated

        file_mtime = os.path.getmtime(filepath)
        file_age = datetime.now() - datetime.fromtimestamp(file_mtime)
        return file_age > timedelta(days=days)

    def load_mac_vendor_list(self):
        """
        Loads the MAC Vendor database from the local JSON file.
        If the file is older than 60 days, fetches a new one.

        Returns:
            list: The parsed MAC Vendor database as a list of dictionaries.
        """
        if self.is_file_older_than(self.vendor_file, 60):
            print("MAC vendor list is outdated or missing. Fetching a new list...")
            self.update_mac_vendor_list()

        try:
            with open(self.vendor_file, "r") as file:
                mac_vendor_list = json.load(file)
                if isinstance(mac_vendor_list, list):
                    return mac_vendor_list
                else:
                    print("Invalid MAC vendor list format.")
                    return []
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading MAC vendor list: {e}")
            return []

    def get_vendor_by_mac(self, mac):
        """
        Identifies the vendor for a given MAC address using the MAC Vendor database.

        Args:
            mac (str): The MAC address to lookup.

        Returns:
            str: The vendor name or 'Unknown' if not found.
        """
        if not mac:
            return "Unknown"
        mac_prefix = mac[:8].upper()  # Extract the first 6 characters of the MAC address
        for entry in self.mac_vendor_list:
            if entry.get("macPrefix", "").upper() == mac_prefix:
                return entry.get("vendorName", "Unknown")
        return "Unknown"

    def ping3_ping(self, ip, timeout=1):
        """
        Sends an ICMP echo request using ping3 and measures latency.

        Args:
            ip (str): The IP address to ping.
            timeout (int): Timeout for the ping request.

        Returns:
            float: Latency in milliseconds if reachable, or None if not reachable.
        """
        try:
            latency = ping(ip, timeout=timeout)
            if latency is not None:
                return round(latency * 1000)  # Convert to milliseconds
            return None  # No response
        except Exception as e:
            print(f"Error pinging {ip}: {e}")
            return None

    async def ping_device(self, ip):
        """
        Pings a device using ping3 to check if it's online and measures latency.

        Args:
            ip (str): The IP address to ping.

        Returns:
            tuple: (ip, latency in milliseconds rounded to nearest integer) if reachable, or (ip, None) if not.
        """
        loop = asyncio.get_event_loop()
        latency = await loop.run_in_executor(None, self.ping3_ping, ip)
        return ip, latency

    async def get_mac_address(self, ip):
        """
        Retrieves the MAC address of a device using ARP packets.

        Args:
            ip (str): The IP address to resolve.

        Returns:
            str: The MAC address, or 'Unknown' if not found.
        """
        try:
            arp_request = ARP(pdst=ip)
            broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
            arp_request_broadcast = broadcast / arp_request
            answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]
            for sent, received in answered_list:
                return received.hwsrc  # Return the MAC address
        except Exception as e:
            print(f"Error retrieving MAC address for {ip}: {e}")
            return "Unknown"

    async def get_netbios_name(self, ip):
        """
        Queries the NetBIOS name of a device.

        Args:
            ip (str): The IP address of the device.

        Returns:
            str: The NetBIOS name, or 'Unknown' if not found.
        """
        try:
            hostname = gethostbyaddr(ip)[0]
            return hostname
        except Exception:
            return "Unknown"

    async def scan_device(self, ip):
        """
        Scans a single device for latency, MAC address, and NetBIOS name.

        Args:
            ip (str): The IP address to scan.

        Returns:
            dict: Information about the device (IP, MAC, Vendor, NetBIOS, Latency).
        """
        print(f"Scanning {ip}...")
        latency = await self.ping_device(ip)

        if latency[1] is not None:  # If the device is reachable
            mac = await self.get_mac_address(ip)
            vendor = self.get_vendor_by_mac(mac)
            netbios = await self.get_netbios_name(ip)

            # Print result immediately
            print(f"{ip}: {latency[1]} ms, MAC: {mac}, Vendor: {vendor}, NetBIOS: {netbios}")
            return {
                'ip': ip,
                'mac': mac,
                'vendor': vendor,
                'netbios': netbios,
                'latency': latency[1]
            }
        else:
            print(f"{ip}: Device not reachable.")
            return None

    async def scan_network(self):
        """
        Scans the network for active devices asynchronously.

        Returns:
            list: A list of dictionaries with device information (IP, MAC, Vendor, NetBIOS, Latency).
        """
        network = ipaddress.IPv4Network(self.subnet, strict=False)
        print(f"Scanning {self.subnet}...")
        tasks = [asyncio.create_task(self.scan_device(str(ip))) for ip in network.hosts()]
        devices = await asyncio.gather(*tasks)
        return [device for device in devices if device]


if __name__ == "__main__":
    # Define the subnet
    subnet = "192.168.1.0/24"

    # Initialize the NetworkScanner
    scanner = NetworkScanner(subnet=subnet)

    # Start the network scan
    devices = asyncio.run(scanner.scan_network())

    # Display summary
    print("\nScan complete.")
    if devices:
        print("\nDevices found on the network:")
        print(f"{'IP Address':<20}{'MAC Address':<20}{'Vendor':<30}{'NetBIOS Name':<40}{'Latency (ms)':<15}")
        print("-" * 125)
        for device in devices:
            print(f"{device['ip']:<20}{device['mac']:<20}{device['vendor']:<30}{device['netbios']:<40}{device['latency']:<15}")
    else:
        print("No devices found.")
