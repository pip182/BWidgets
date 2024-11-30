import sys
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from ping3 import ping
from collections import deque

# Constants
TARGET_HOST = "google.com"
MAX_X = 180  # Number of data points to display
INTERVAL = 1000  # Update interval in milliseconds
IRREGULAR_LATENCY_FACTOR = 3  # Threshold multiplier for irregular latency

# Data storage
latency_data = deque([0] * MAX_X, maxlen=MAX_X)
lost_packets = 0
total_packets = 0
irregular_latency_count = 0  # Counter for irregular latencies


# Main Application Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Latency Monitor with Line Chart")
        self.setGeometry(100, 100, 800, 600)

        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main Layout
        self.main_layout = QVBoxLayout(self.central_widget)

        # Initialize the line chart
        self.series = QLineSeries()
        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setTitle(f"Latency Monitoring to {TARGET_HOST}")

        # Configure axes
        self.axisX = QValueAxis()
        self.axisX.setTitleText("Time")
        self.axisX.setRange(0, MAX_X)
        self.chart.addAxis(self.axisX, Qt.AlignBottom)
        self.series.attachAxis(self.axisX)

        self.axisY = QValueAxis()
        self.axisY.setTitleText("Latency (ms)")
        self.chart.addAxis(self.axisY, Qt.AlignLeft)
        self.series.attachAxis(self.axisY)

        # Chart view
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.main_layout.addWidget(self.chart_view)

        # Labels for statistics
        self.label_layout = QHBoxLayout()
        self.sent_label = QLabel("Packets Sent: 0")
        self.lost_label = QLabel("Packets Lost: 0")
        self.avg_latency_label = QLabel("Average Latency: 0 ms")
        self.irregular_label = QLabel("Irregular Latencies: 0")
        self.label_layout.addWidget(self.sent_label)
        self.label_layout.addWidget(self.lost_label)
        self.label_layout.addWidget(self.avg_latency_label)
        self.label_layout.addWidget(self.irregular_label)

        # Add the label layout to the main layout
        self.main_layout.addLayout(self.label_layout)

        # Timer for Updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(INTERVAL)

        # Decoration toggle
        self.is_decorated = True
        self.central_widget.setFocusPolicy(Qt.StrongFocus)
        self.central_widget.keyPressEvent = self.keyPressEvent

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F5:
            self.is_decorated = not self.is_decorated
            self.setWindowFlags(Qt.FramelessWindowHint if not self.is_decorated else Qt.Window)
            self.show()

    def update_plot(self):
        global total_packets, lost_packets, irregular_latency_count

        # Ping the target host and collect latency data
        latency = ping(TARGET_HOST, timeout=1)
        total_packets += 1

        if latency is None:
            lost_packets += 1
            latency_data.append(0)  # Show 0 latency for lost packets
        else:
            latency_ms = latency * 1000  # Convert to ms
            latency_data.append(latency_ms)

            # Calculate average latency
            avg_latency = sum([x for x in latency_data if x > 0]) / len(
                [x for x in latency_data if x > 0]
            ) if latency_data else 0

            # Check if latency is irregular
            if latency_ms > IRREGULAR_LATENCY_FACTOR * avg_latency:
                irregular_latency_count += 1

        # Update the line series with new data
        self.series.clear()
        for i, latency in enumerate(latency_data):
            self.series.append(i, latency)

        # Dynamically update Y-axis range
        max_latency = max(latency_data)
        self.axisY.setRange(0, max_latency * 1.2 if max_latency > 0 else 200)  # Add some headroom

        # Update labels
        self.sent_label.setText(f"Packets Sent: {total_packets}")
        self.lost_label.setText(f"Packets Lost: {lost_packets}")
        self.avg_latency_label.setText(f"Average Latency: {avg_latency:.2f} ms")
        self.irregular_label.setText(f"Irregular Latencies: {irregular_latency_count}")


# Run the application
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
