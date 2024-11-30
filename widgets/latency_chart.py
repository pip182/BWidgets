
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from ping3 import ping
from collections import deque


class LatencyChartWidget(QWidget):
    """Widget to monitor latency using a line chart."""

    def __init__(self, target_host, max_x=180, interval=1000, irregular_factor=3):
        super().__init__()
        self.target_host = target_host
        self.max_x = max_x
        self.interval = interval
        self.irregular_factor = irregular_factor

        # Data storage
        self.latency_data = deque([0] * max_x, maxlen=max_x)
        self.lost_packets = 0
        self.total_packets = 0
        self.irregular_latency_count = 0

        # Main Layout
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        # Initialize the line chart
        self.series = QLineSeries()
        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setTitle(f"Latency Monitoring to {self.target_host}")

        # Configure axes
        self.axisX = QValueAxis()
        self.axisX.setTitleText("Time")
        self.axisX.setRange(0, self.max_x)
        self.chart.addAxis(self.axisX, Qt.AlignBottom)
        self.series.attachAxis(self.axisX)

        self.axisY = QValueAxis()
        self.axisY.setTitleText("Latency (ms)")
        self.axisY.setRange(0, 200)
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

        # Timer for updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(self.interval)

    def update_plot(self):
        """Ping the target host and update the chart."""
        latency = ping(self.target_host, timeout=1)
        self.total_packets += 1

        if latency is None:
            self.lost_packets += 1
            self.latency_data.append(0)
        else:
            latency_ms = latency * 1000  # Convert to milliseconds
            self.latency_data.append(latency_ms)

            # Calculate average latency for non-zero values
            valid_latencies = [x for x in self.latency_data if x > 0]
            avg_latency = sum(valid_latencies) / len(valid_latencies) if valid_latencies else 0

            # Check for irregular latency
            if latency_ms > self.irregular_factor * avg_latency:
                self.irregular_latency_count += 1

        # Update the series
        self.series.clear()
        for i, latency in enumerate(self.latency_data):
            self.series.append(i, latency)

        # Dynamically adjust Y-axis range
        max_latency = max(self.latency_data)
        self.axisY.setRange(0, max_latency * 1.2 if max_latency > 0 else 200)

        # Update labels
        self.sent_label.setText(f"Packets Sent: {self.total_packets}")
        self.lost_label.setText(f"Packets Lost: {self.lost_packets}")
        self.avg_latency_label.setText(
            f"Average Latency: {avg_latency:.2f} ms"
        )
        self.irregular_label.setText(
            f"Irregular Latencies: {self.irregular_latency_count}"
        )
