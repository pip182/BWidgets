# gui.py
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, QThreadPool
from PyQt6.QtGui import QFont
import local_config
from monitor import DeviceMonitor


class DraggableStyledWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the window
        self.setWindowTitle("System Monitor & Device Status")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setWindowOpacity(0.9)

        # Set up the monitor
        self.monitor = DeviceMonitor(local_config.devices)
        self.monitor.devices_checked.connect(self.update_table)
        self.monitor.error_occurred.connect(self.handle_error)

        # Set up layout
        main_layout = QVBoxLayout(self)
        top_layout = QHBoxLayout()
        self.title_label = QLabel("System Monitor & Device Status")
        title_font = QFont()
        title_font.setPointSize(12)
        self.title_label.setFont(title_font)
        self.close_button = QPushButton(self)
        self.close_button.setText("X")
        self.close_button.clicked.connect(self.close)
        top_layout.addWidget(self.title_label)
        top_layout.addWidget(self.close_button)
        main_layout.addLayout(top_layout)

        # System info label
        self.system_info_label = QLabel("Fetching system and device info...")
        main_layout.addWidget(self.system_info_label)

        # Device status table
        self.table = QTableWidget(self)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Device Name", "Resource", "Type", "Value", "Status", "Response Time (ms)"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.table)

        # Thread pool and timers
        self.threadpool = QThreadPool()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run_device_check)
        self.timer.start(60000)

        # Initial device check
        self.run_device_check()

    def run_device_check(self):
        self.monitor.check_devices()

    def update_table(self, updated_devices):
        self.table.setRowCount(0)
        for device_name, resources in updated_devices.items():
            for resource_name, status_info in resources.items():
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(device_name))
                self.table.setItem(row, 1, QTableWidgetItem(resource_name))
                self.table.setItem(row, 2, QTableWidgetItem(self.get_resource_type(device_name, resource_name)))
                self.table.setItem(row, 3, QTableWidgetItem("Value"))
                status_item = QTableWidgetItem(status_info['status'])
                self.table.setItem(row, 4, status_item)
                response_time_item = QTableWidgetItem(str(status_info['response_time']) if status_info['response_time'] else "N/A")
                self.table.setItem(row, 5, response_time_item)

    def handle_error(self, error_message):
        print(f"Error: {error_message}")

    def get_resource_type(self, device_name, resource_name):
        # Add logic to determine resource type from devices configuration
        return "Unknown"
