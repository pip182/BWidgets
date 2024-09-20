import sys
from PyQt6.QtCore import Qt, QTimer, QRunnable, QThreadPool, pyqtSlot, QSize, QObject, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QStyle,
)
import os
import platform
import subprocess
import requests
import socket
import time
import psutil
from plyer import notification
import local_config  # Ensure this file exists and is correctly structured
import logging

# Configure logging
logging.basicConfig(
    filename='device_status.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Constants
UPDATE_DELAY = 1000  # 1 second
NETWORK_UPDATE_MULTIPLIER = 5  # 5 seconds
DEVICE_CHECK_MULTIPLIER = 1  # 1 minute for quicker testing
ONLINE = "Online"
OFFLINE = "Offline"

DEVICE_CHECK_DELAY = DEVICE_CHECK_MULTIPLIER * 60 * 1000  # in milliseconds

devices = local_config.devices  # Load devices from config


def get_size(bytes):
    """Convert bytes to a human-readable format."""
    for unit in ['', 'K', 'M', 'G', 'T']:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}B"
        bytes /= 1024
    return f"{bytes:.2f}P"


class WorkerSignals(QObject):
    result = pyqtSignal(object)
    error = pyqtSignal(str)


class Worker(QRunnable):
    """
    Worker thread for executing tasks asynchronously.
    """
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        """
        Execute the function and emit the result via signal.
        """
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except Exception as e:
            error_message = f"Error in Worker.run(): {e}"
            print(error_message)
            logging.error(error_message)
            self.signals.error.emit(str(e))


class DraggableStyledWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Assign object name
        self.setObjectName("main_widget")

        # Apply stylesheet
        self.setStyleSheet("""
            QWidget#main_widget {
                background-color: rgba(0, 0, 0, 180);
                border-radius: 10px;
                color: white;
                padding: 10px;
                border: 2px solid rgba(55, 55, 55, 180);
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 50);
                border-radius: 5px;
            }
            QLabel {
                background-color: transparent;
            }
            QTableWidget {
                background-color: rgba(255, 255, 255, 50);
                color: white;
                border: none;
                gridline-color: rgba(255, 255, 255, 100);
            }
            QHeaderView::section {
                background-color: rgba(55, 55, 55, 180);
                color: white;
                padding: 4px;
                border: 1px solid rgba(255, 255, 255, 100);
            }
        """)

        # Window settings
        self.setWindowTitle("Styled Draggable Desktop Widget")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint
        )
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)

        # Initialize dictionaries
        self.last_status = {}
        self.notification_cooldown = {}
        self.table_rows = {}  # Mapping: (device_name, resource_name) -> row_index
        self.data = {
            "cpu_usage": 0,
            "memory_usage": "0B",
            "total_memory": "0B",
            "upload_speed": "0B/s",
            "download_speed": "0B/s",
            "devices": {}
        }

        # Set up layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Top layout with title and close button
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)

        self.title_label = QLabel("System Monitor & Device Status", self)
        title_font = QFont()
        title_font.setPointSize(12)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: white; background-color: transparent;")

        spacer = QWidget(self)
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        spacer.setStyleSheet("background-color: transparent; border: none;")

        self.close_button = QPushButton(self)
        self.close_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton))
        self.close_button.setIconSize(QSize(16, 16))
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 50);
                border-radius: 5px;
            }
        """)
        self.close_button.clicked.connect(self.close)

        top_layout.addWidget(self.title_label)
        top_layout.addWidget(spacer)
        top_layout.addWidget(self.close_button)

        # System info label
        self.system_info_label = QLabel("Fetching system and device info...", self)
        self.system_info_label.setFont(title_font)
        self.system_info_label.setStyleSheet("""
            background-color: rgba(0, 0, 0, 180);
            border-radius: 10px;
            color: white;
            padding: 10px;
            border: 2px solid rgba(55, 55, 55, 180);
        """)
        self.system_info_label.setWordWrap(True)

        # Device status table
        self.table = QTableWidget(self)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Device Name", "Resource", "Type", "Value", "Status", "Response Time (ms)"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setStretchLastSection(True)

        # Add widgets to main layout
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.system_info_label)
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

        # Initialize system info variables
        self.prev_sent = psutil.net_io_counters().bytes_sent
        self.prev_recv = psutil.net_io_counters().bytes_recv

        # Set up thread pool
        self.threadpool = QThreadPool()
        print(f"Multithreading with maximum {self.threadpool.maxThreadCount()} threads")  # Debug

        # Set up timers
        self.timer_general_info = QTimer(self)
        self.timer_general_info.timeout.connect(self.run_general_info_task)
        self.timer_general_info.start(UPDATE_DELAY)

        self.timer_network_info = QTimer(self)
        self.timer_network_info.timeout.connect(self.run_network_info_task)
        self.timer_network_info.start(UPDATE_DELAY * NETWORK_UPDATE_MULTIPLIER)

        self.timer_device_check = QTimer(self)
        self.timer_device_check.timeout.connect(self.run_check_devices_task)
        self.timer_device_check.start(DEVICE_CHECK_DELAY)

        # Enable dragging
        self.oldPos = self.pos()

        # Perform initial device check
        self.run_check_devices_task()

    # Draggable functionality
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()

    def run_general_info_task(self):
        worker = Worker(self.update_system_info)
        self.threadpool.start(worker)

    def run_network_info_task(self):
        worker = Worker(self.update_network_speed)
        self.threadpool.start(worker)

    def run_check_devices_task(self):
        """
        Run the check_devices method asynchronously and handle the results via signals.
        """
        print("Submitting check_devices task to thread pool")  # Debug
        worker = Worker(self.check_devices)
        worker.signals.result.connect(self.handle_device_check_result)
        worker.signals.error.connect(self.handle_worker_error)
        self.threadpool.start(worker)

    def handle_worker_error(self, error_message):
        """
        Handle errors emitted by the Worker.
        """
        print(f"Worker encountered an error: {error_message}")  # Debug
        logging.error(f"Worker encountered an error: {error_message}")

    def handle_device_check_result(self, updated_devices):
        """
        Callback function to handle the results from the asynchronous check_devices.
        Updates the UI and sends notifications if necessary.
        """
        print("Received updated devices data from check_devices")  # Debug
        self.data["devices"] = updated_devices
        self.update_table()
        self.update_label()

    def update_system_info(self):
        try:
            self.data["cpu_usage"] = psutil.cpu_percent(interval=0.5)
            memory_info = psutil.virtual_memory()
            self.data["memory_usage"] = get_size(memory_info.used)
            self.data["total_memory"] = get_size(memory_info.total)
        except Exception as e:
            print(f"Error updating system info: {e}")
            logging.error(f"Error updating system info: {e}")
            self.data["cpu_usage"] = "N/A"
            self.data["memory_usage"] = "N/A"
            self.data["total_memory"] = "N/A"
        self.update_label()

    def update_network_speed(self):
        try:
            net_io = psutil.net_io_counters()
            upload_speed = net_io.bytes_sent - self.prev_sent
            download_speed = net_io.bytes_recv - self.prev_recv
            self.prev_sent = net_io.bytes_sent
            self.prev_recv = net_io.bytes_recv
            self.data["upload_speed"] = get_size(upload_speed / NETWORK_UPDATE_MULTIPLIER)
            self.data["download_speed"] = get_size(download_speed / NETWORK_UPDATE_MULTIPLIER)
        except Exception as e:
            print(f"Error updating network speed: {e}")
            logging.error(f"Error updating network speed: {e}")
            self.data["upload_speed"] = "N/A/s"
            self.data["download_speed"] = "N/A/s"
        self.update_label()

    def check_devices(self):
        """
        Perform device checks and return the updated devices data.
        This method runs in a separate thread.
        """
        updated_devices = {}
        for device_name, resources in devices.items():
            print(f"Checking device: {device_name}")  # Debug
            if device_name not in self.data["devices"]:
                self.data["devices"][device_name] = {}
            device_data = {}

            # Check URLs
            for url_info in resources.get("urls", []):
                resource_name = url_info['name']
                current_status, response_time = self.check_http(url_info, device_name)
                print(f"  Checking URL resource: {resource_name} - Status: {current_status}, Response Time: {response_time} ms")  # Debug
                key = (device_name, resource_name)
                last_status = self.last_status.get(key)
                current_time = time.time()
                cooldown_time = 60  # seconds

                if last_status is not None and last_status != current_status:
                    last_notified = self.notification_cooldown.get(key, 0)
                    if current_time - last_notified > cooldown_time:
                        # Status changed, send notification
                        notification.notify(
                            title=f"Device Status Change: {device_name}",
                            message=f"{resource_name} is now {current_status}",
                            app_name="Device Monitor",
                            timeout=5  # Duration in seconds
                        )
                        # Update cooldown
                        self.notification_cooldown[key] = current_time

                        # Log the status change
                        logging.info(f"{device_name} - {resource_name} status changed to {current_status}")

                # Update last_status
                self.last_status[key] = current_status
                # Update device_data
                device_data[resource_name] = {"status": current_status, "response_time": response_time}

            # Check IPs
            for ip_info in resources.get("ips", []):
                resource_name = ip_info['name']
                if 'ports' in ip_info:
                    current_status, response_time = self.check_port(ip_info, device_name)
                else:
                    current_status, response_time = self.ping_device(ip_info, device_name)
                print(f"  Checking IP resource: {resource_name} - Status: {current_status}, Response Time: {response_time} ms")
                key = (device_name, resource_name)
                last_status = self.last_status.get(key)
                current_time = time.time()
                cooldown_time = 60  # seconds

                if last_status is not None and last_status != current_status:
                    last_notified = self.notification_cooldown.get(key, 0)
                    if current_time - last_notified > cooldown_time:
                        # Status changed, send notification
                        notification.notify(
                            title=f"Device Status Change: {device_name}",
                            message=f"{resource_name} is now {current_status}",
                            app_name="Device Monitor",
                            timeout=5
                        )
                        # Update cooldown
                        self.notification_cooldown[key] = current_time

                        # Log the status change
                        logging.info(f"{device_name} - {resource_name} status changed to {current_status}")

                # Update last_status
                self.last_status[key] = current_status
                # Update device_data
                device_data[resource_name] = {"status": current_status, "response_time": response_time}

            # Check directories
            for directory_info in resources.get("directories", []):
                resource_name = directory_info['name']
                current_status, response_time = self.check_directory(directory_info, device_name)
                print(f"  Checking Directory resource: {resource_name} - Status: {current_status}, Response Time: {response_time} ms")  # Debug
                key = (device_name, resource_name)
                last_status = self.last_status.get(key)
                current_time = time.time()
                cooldown_time = 60  # seconds

                if last_status is not None and last_status != current_status:
                    last_notified = self.notification_cooldown.get(key, 0)
                    if current_time - last_notified > cooldown_time:
                        # Status changed, send notification
                        notification.notify(
                            title=f"Device Status Change: {device_name}",
                            message=f"{resource_name} is now {current_status}",
                            app_name="Device Monitor",
                            timeout=5
                        )
                        # Update cooldown
                        self.notification_cooldown[key] = current_time

                        # Log the status change
                        logging.info(f"{device_name} - {resource_name} status changed to {current_status}")

                # Update last_status
                self.last_status[key] = current_status
                # Update device_data
                device_data[resource_name] = {"status": current_status, "response_time": response_time}

            # Assign device_data to updated_devices
            updated_devices[device_name] = device_data

        # Print the updated_devices
        print(f"Updated devices data: {updated_devices}")  # Debug

        # Return the updated devices data
        return updated_devices

    def ping_device(self, ip_info, device_name):
        """Ping a device and return its status and response time."""
        ip = ip_info['value']
        print(f"Starting ping check for {device_name} ({ip_info['name']}) - {ip}")
        try:
            start_time = time.time()
            command = ["ping", "-n", "1", ip] if platform.system().lower() == "windows" else ["ping", "-c", "1", ip]
            ping = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            end_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            end_time = round(end_time, 2)
            if ping.returncode != 0 or 'unreachable' in ping.stdout.decode().lower():
                print(f"    {device_name} ({ip_info['name']}) - {OFFLINE}")
                return OFFLINE, None
            else:
                print(f"    {device_name} ({ip_info['name']}) - {ONLINE} ({end_time:.2f}ms)")
                return ONLINE, end_time
        except Exception as e:
            print(f"    {device_name} ({ip_info['name']}) - {OFFLINE} - Error: {e}")
            return OFFLINE, None

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
            print(f"Error checking HTTP for {device_name} ({url}): {e}")
            logging.error(f"Error checking HTTP for {device_name} ({url}): {e}")
            return OFFLINE, None

    def check_port(self, ip_info, device_name):
        """Check specified ports and return status."""
        ip = ip_info['value']
        port_statuses = []
        for port in ip_info['ports']:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)  # 3 seconds timeout
                start_time = time.time()
                result = sock.connect_ex((ip, port))
                response_time = (time.time() - start_time) * 1000  # ms
                response_time = round(response_time, 2)
                sock.close()
                if result == 0:
                    port_statuses.append((ONLINE, response_time))
                else:
                    port_statuses.append((OFFLINE, None))
            except Exception as e:
                print(f"Error checking port {port} for {device_name} ({ip}): {e}")
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
            print(f"Error checking directory {directory} for {device_name}: {e}")
            logging.error(f"Error checking directory {directory} for {device_name}: {e}")
            return OFFLINE, None

    def update_label(self):
        """Update the label with system information."""
        # System Info
        system_info = (
            f"CPU Usage: {self.data['cpu_usage']}%\n"
            f"Memory Usage: {self.data['memory_usage']} / {self.data['total_memory']}\n"
            f"Upload Speed: {self.data['upload_speed']}/s\n"
            f"Download Speed: {self.data['download_speed']}/s\n"
        )

        self.system_info_label.setText(system_info)

    def update_table(self):
        """Update the device status table with the latest data."""
        print("Updating table with device data")  # Debug
        # Keep track of existing keys to identify removed entries
        existing_keys = set(self.table_rows.keys())
        updated_keys = set()

        for device_name, resources in self.data["devices"].items():
            print(f"  Device: {device_name}")  # Debug
            for resource_name, status_info in resources.items():
                key = (device_name, resource_name)
                updated_keys.add(key)

                # Check if the key exists in the mapping
                if key in self.table_rows:
                    row = self.table_rows[key]
                    print(f"    Updating existing resource: {resource_name}")  # Debug
                else:
                    # Insert a new row
                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    self.table_rows[key] = row
                    print(f"    Inserting new resource: {resource_name}")  # Debug

                # Device Name
                device_item = QTableWidgetItem(device_name)
                device_item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # Make item read-only
                self.table.setItem(row, 0, device_item)

                # Resource Name
                resource_item = QTableWidgetItem(resource_name)
                resource_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(row, 1, resource_item)

                # Type (Determine based on device config)
                resource_type = self.get_resource_type(device_name, resource_name)
                type_item = QTableWidgetItem(resource_type)
                type_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(row, 2, type_item)

                # Value
                value = self.get_resource_value(device_name, resource_name)
                value_item = QTableWidgetItem(value)
                value_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(row, 3, value_item)

                # Status
                status = status_info["status"]
                status_item = QTableWidgetItem(status)
                status_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                # Color coding for status
                if status == ONLINE:
                    status_item.setForeground(Qt.GlobalColor.green)
                else:
                    status_item.setForeground(Qt.GlobalColor.red)
                self.table.setItem(row, 4, status_item)

                # Response Time
                response_time = status_info["response_time"]
                if response_time:
                    response_time_str = f"{response_time:.2f}"
                else:
                    response_time_str = "N/A"
                response_time_item = QTableWidgetItem(response_time_str)
                response_time_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(row, 5, response_time_item)

        # Optional: Remove rows that are no longer present
        keys_to_remove = existing_keys - updated_keys
        for key in keys_to_remove:
            row = self.table_rows[key]
            self.table.removeRow(row)
            del self.table_rows[key]
            print(f"  Removed resource: {key[1]} from device: {key[0]}")  # Debug

        # Re-map the row indices if rows have been removed
        if keys_to_remove:
            self.reindex_table_rows()

    def reindex_table_rows(self):
        """Reindex the table_rows mapping after rows have been removed."""
        new_table_rows = {}
        for row in range(self.table.rowCount()):
            device_item = self.table.item(row, 0)
            resource_item = self.table.item(row, 1)
            if device_item and resource_item:
                device_name = device_item.text()
                resource_name = resource_item.text()
                key = (device_name, resource_name)
                new_table_rows[key] = row
        self.table_rows = new_table_rows
        print("Reindexed table rows after removal.")  # Debug

    def get_resource_type(self, device_name, resource_name):
        """Determine the type of the resource based on the config."""
        device_resources = devices.get(device_name, {})
        for res_type in ["urls", "ips", "directories"]:
            for res in device_resources.get(res_type, []):
                if res['name'] == resource_name:
                    return res_type[:-1].capitalize()  # Remove the trailing 's' and capitalize
        return "Unknown"

    def get_resource_value(self, device_name, resource_name):
        """Retrieve the value of the resource from the config."""
        device_resources = devices.get(device_name, {})
        for res_type in ["urls", "ips", "directories"]:
            for res in device_resources.get(res_type, []):
                if res['name'] == resource_name:
                    return res['value']
        return "N/A"


# Start the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DraggableStyledWidget()
    window.show()
    sys.exit(app.exec())
