from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, QTimer
from collections import deque
from widgets.base_widget import BaseWidget


class LatencyChartWidget(BaseWidget):
    def __init__(
        self,
        target_host,
        interval=1000,
        max_x=180,
        irregular_factor=3,
        results_handler=None,
        data_provider=None,
        alignment="center",
        margins=None,
        style=None,
        *args,
        **kwargs,
    ):
        super().__init__(
            alignment=alignment,
            margins=margins,
            data_provider=data_provider,
            results_handler=results_handler,
            interval=interval,
            widget_type="latency_chart",
            widget_name=kwargs.get("name"),
            *args,
            **kwargs,
        )
        self.target_host = target_host
        self.interval = interval
        self.max_x = max_x
        self.irregular_factor = irregular_factor
        self.style = style or {}

        # Initialize latency data storage
        self.latency_data = deque([0] * max_x, maxlen=max_x)

        # Set up chart
        self.chart = QChart()
        self.series = QLineSeries()
        self.chart.addSeries(self.series)
        self.chart.setTitle(f"Latency Monitoring to {self.target_host}")

        # Configure axes
        self.axisX = QValueAxis()
        self.axisX.setTitleText("Time")
        self.axisX.setRange(0, max_x)
        self.chart.addAxis(self.axisX, Qt.AlignBottom)
        self.series.attachAxis(self.axisX)

        self.axisY = QValueAxis()
        self.axisY.setTitleText("Latency (ms)")
        self.axisY.setRange(0, 200)
        self.chart.addAxis(self.axisY, Qt.AlignLeft)
        self.series.attachAxis(self.axisY)

        # Apply style settings
        if "color" in self.style:
            self.series.setColor(QColor(self.style["color"]))

        # Chart View
        self.chart_view = QChartView(self.chart)
        self.add_child_widget(self.chart_view)

        # Timer for periodic updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.periodic_task)
        self.timer.start(self.interval)

    def on_data_fetched(self, data):
        """Callback for processing fetched data."""
        if isinstance(data, (int, float)):  # Ensure data is numeric
            self.latency_data.append(data)
        else:
            self.log("Invalid data type received for latency chart.")

        # Update series with new data
        self.series.clear()
        for i, value in enumerate(self.latency_data):
            self.series.append(i, value)

        # Adjust Y-axis dynamically
        max_latency = max(self.latency_data)
        self.axisY.setRange(0, max(max_latency * 1.2, 200))

    def periodic_task(self):
        """Fetch new data and refresh the chart."""
        self.defer_data_fetching()
