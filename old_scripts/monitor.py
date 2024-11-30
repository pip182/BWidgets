# monitor.py
import time
import logging
import socket
import subprocess
import platform
import requests
import os
import psutil
from PyQt6.QtCore import QObject, pyqtSignal

# Constants
ONLINE = "Online"
OFFLINE = "Offline"


class DeviceMonitor(QObject):
    """Class to handle device monitoring functionality."""

    # Signals to communicate with the GUI
    devices_checked = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, devices):
        super().__init__()
        self.devices = devices
        self.last_status = {}
        self.notification_cooldown = {}

    def get_size(self, bytes):
        """Convert bytes to a human-readable format."""
        for unit in ['', 'K', 'M', 'G', 'T']:
            if bytes < 1024:
                return f"{bytes:.2f}{unit}B"
            bytes /= 1024
        return f"{bytes:.2f}P"

    def check_devices(self):
        """Perform device checks and return the updated devices data."""
        updated_devices = {}
        for device_name, resources in self.devices.items():
            device_data = {}

            # Check URLs
            for url_info in resources.get("urls", []):
                resource_name = url_info['name']
                current_status, response_time = self.check_http(url_info, device_name)
                key = (device_name, resource_name)
                self.last_status[key] = current_status
                device_data[resource_name] = {"status": current_status, "response_time": response_time}

            # Check IPs
            for ip_info in resources.get("ips", []):
                resource_name = ip_info['name']
                if 'ports' in ip_info:
                    current_status, response_time = self.check_port(ip_info, device_name)
                else:
                    current_status, response_time = self.ping_device(ip_info, device_name)
                key = (device_name, resource_name)
                self.last_status[key] = current_status
                device_data[resource_name] = {"status": current_status, "response_time": response_time}

            # Check directories
            for directory_info in resources.get("directories", []):
                resource_name = directory_info['name']
                current_status, response_time = self.check_directory(directory_info, device_name)
                key = (device_name, resource_name)
                self.last_status[key] = current_status
                device_data[resource_name] = {"status": current_status, "response_time": response_time}

            updated_devices[device_name] = device_data

        # Emit the results back to the GUI
        self.devices_checked.emit(updated_devices)

    def check_http(self, url_info, device_name):
        """Check HTTP response and return its status and response time."""
        url = url_info['value']
        try:
            start_time = time.time()
            response = requests.get(url, timeout=5)
            response_time = (time.time() - start_time) * 1000  # ms
            if response.status_code == 200:
                return ONLINE, round(response_time, 2)
            else:
                return OFFLINE, None
        except Exception as e:
            logging.error(f"Error checking HTTP for {device_name} ({url}): {e}")
            return OFFLINE, None

    def ping_device(self, ip_info, device_name):
        """Ping a device and return its status and response time."""
        ip = ip_info['value']
        try:
            start_time = time.time()
            command = ["ping", "-n", "1", ip] if platform.system().lower() == "windows" else ["ping", "-c", "1", ip]
            ping = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            if ping.returncode == 0:
                return ONLINE, round(response_time, 2)
            else:
                return OFFLINE, None
        except Exception as e:
            logging.error(f"Error pinging device {device_name} ({ip}): {e}")
            return OFFLINE, None

    def check_port(self, ip_info, device_name):
        """Check specified ports and return status."""
        ip = ip_info['value']
        port_statuses = []
        for port in ip_info['ports']:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                start_time = time.time()
                result = sock.connect_ex((ip, port))
                response_time = (time.time() - start_time) * 1000  # ms
                sock.close()
                if result == 0:
                    port_statuses.append((ONLINE, round(response_time, 2)))
                else:
                    port_statuses.append((OFFLINE, None))
            except Exception as e:
                logging.error(f"Error checking port {port} for {device_name} ({ip}): {e}")
                port_statuses.append((OFFLINE, None))
        return port_statuses[0] if port_statuses else (OFFLINE, None)

    def check_directory(self, directory_info, device_name):
        """Check if directory exists and return its status."""
        directory = directory_info['value']
        try:
            if os.path.exists(directory):
                return ONLINE, None
            else:
                return OFFLINE, None
        except Exception as e:
            logging.error(f"Error checking directory {directory} for {device_name}: {e}")
            return OFFLINE, None
