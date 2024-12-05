import asyncio
import platform
import subprocess
import ipaddress
from socket import gethostbyaddr

is_windows = platform.system().lower() == "windows"


async def ping_device(ip):
    """
    Pings a device to check if it's online and measures latency.

    Args:
        ip (str): The IP address to ping.

    Returns:
        tuple: (ip, latency in milliseconds) if reachable, or (ip, None) if not.
    """
    param = "-n 1" if is_windows else "-c 1"
    cmd = f"ping {param} -w 500 {ip}"
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL
        )
        stdout, _ = await proc.communicate()
        result = stdout.decode()
        if proc.returncode == 0:
            if is_windows:
                start = result.find("time=")
                if start != -1:
                    latency = result[start + 5:result.find("ms", start)].strip()
                    return ip, float(latency)
            else:
                start = result.find("time=")
                if start != -1:
                    latency = result[start + 5:result.find(" ", start)].strip()
                    return ip, float(latency)
    except Exception:
        pass
    return ip, None


async def get_mac_address(ip):
    """
    Retrieves the MAC address of a device using the ARP table.

    Args:
        ip (str): The IP address to resolve.

    Returns:
        str: The MAC address, or 'Unknown' if not found.
    """
    try:
        if is_windows:
            arp_result = subprocess.check_output("arp -a", shell=True).decode()
            for line in arp_result.splitlines():
                if ip in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        return parts[1]  # Extract the MAC address
        else:
            arp_result = subprocess.check_output(["arp", "-n", ip], stderr=subprocess.DEVNULL).decode()
            for line in arp_result.splitlines():
                if ip in line:
                    return line.split()[2]  # Extract the MAC address
    except (subprocess.CalledProcessError, IndexError):
        print("Error retrieving MAC address.")
        pass
    return "Unknown"


async def get_netbios_name(ip):
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


async def scan_device(ip):
    """
    Scans a single device for latency, MAC address, and NetBIOS name.

    Args:
        ip (str): The IP address to scan.

    Returns:
        dict: Information about the device (IP, MAC, NetBIOS, Latency).
    """
    print(f"Scanning {ip}...")
    latency = await ping_device(ip)
    if latency[1] is not None:  # If the device is reachable
        mac = await get_mac_address(ip)
        netbios = await get_netbios_name(ip)
        rtn = {'ip': ip, 'mac': mac, 'netbios': netbios, 'latency': latency[1]}
        print(f"{ip}: Found device: {rtn}")
        return rtn
    else:
        print(f"{ip}: Device not found.")
        return None


async def scan_network(ip_range):
    """
    Scans the network for active devices asynchronously.

    Args:
        ip_range (str): CIDR notation of the IP range to scan, e.g., "192.168.1.0/24".

    Returns:
        list: A list of dictionaries with device information (IP, MAC, NetBIOS, Latency).
    """
    network = ipaddress.IPv4Network(ip_range, strict=False)
    print(f"Scanning {ip_range}...")
    tasks = [scan_device(str(ip)) for ip in network.hosts()]
    devices = await asyncio.gather(*tasks)
    return [device for device in devices if device]


if __name__ == "__main__":
    import time

    # Change this to your network's CIDR notation
    subnet = "192.168.1.0/24"

    # Validate subnet format
    try:
        ipaddress.IPv4Network(subnet)
    except ValueError:
        print("Invalid subnet format. Please enter a valid CIDR range (e.g., 192.168.1.0/24).")
        exit(1)

    start_time = time.time()
    devices = asyncio.run(scan_network(subnet))
    end_time = time.time()

    # Display results
    if devices:
        print("\nDevices found on the network:")
        print(f"{'IP Address':<20}{'MAC Address':<20}{'NetBIOS Name':<20}{'Latency (ms)':<15}")
        print("-" * 75)
        for device in devices:
            print(f"{device['ip']:<20}{device['mac']:<20}{device['netbios']:<20}{device['latency']:<15}")
    else:
        print("No devices found. Ensure the subnet is correct and devices are online.")

    print(f"\nScan completed in {end_time - start_time:.2f} seconds.")
