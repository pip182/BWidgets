from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPainter
from widgets.base_widget import BaseWidget
from ping3 import ping
from collections import deque


class LatencyChartWidget(BaseWidget):
    def __init__(self, target_host, max_x=180, interval=1000, irregular_factor=3, alignment="center", margins=None, style=None, *args, **kwargs):
        self.target_host = target_host
        self.latency_data = deque([0] * max_x, maxlen=max_x)
        self.series = QLineSeries()
        self.chart = QChart()
        self.timer = QTimer()

        # Set up the chart
        self.chart.addSeries(self.series)
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        # Set up axes
        self.axis_x = QValueAxis()
        self.axis_x.setTitleText("Time")
        self.axis_x.setRange(0, max_x)
        self.axis_y = QValueAxis()
        self.axis_y.setTitleText("Latency (ms)")
        self.axis_y.setRange(0, 200)
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_x)
        self.series.attachAxis(self.axis_y)

        # Start the timer
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(interval)

        super().__init__(self.chart_view, alignment=alignment, margins=margins, style=style, *args, **kwargs)

    def update_plot(self):
        latency = ping(self.target_host, timeout=1)
        self.latency_data.append(latency * 1000 if latency else 0)

        # Update chart series
        self.series.clear()
        for i, latency in enumerate(self.latency_data):
            self.series.append(i, latency)

        # Adjust Y-axis dynamically
        max_latency = max(self.latency_data)
        self.axis_y.setRange(0, max_latency * 1.2 if max_latency > 0 else 200)
