from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from widgets.base_widget import BaseWidget
import importlib


class Table(BaseWidget):
    def __init__(self, data=None, columns=None, data_provider=None, refresh_interval=None, alignment="center", margins=None, style=None, *args, **kwargs):
        """
        Create a Table widget.

        Args:
            data: Static list of rows for the table (optional).
            columns: List of columns to display (optional).
            data_provider: A string specifying a function to fetch dynamic data (optional).
            refresh_interval: Interval in milliseconds to refresh the data (optional).
            alignment: Alignment of the widget.
            margins: Margins for the widget.
            style: CSS-like styles for the widget.
        """
        self.table = QTableWidget()
        self.columns = columns
        self.data_provider = data_provider
        self.refresh_interval = refresh_interval

        # Fetch data from the provider if specified
        if data_provider:
            data = self.fetch_data()

        # Populate the table
        if data:
            self.populate_table(data)

        # Adjust table settings
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Start refresh timer if interval is provided
        if refresh_interval and data_provider:
            print(f"Starting data refresh timer with interval {refresh_interval} ms")
            self.timer = QTimer()
            self.timer.timeout.connect(self.refresh_data)
            self.timer.start(refresh_interval)

        super().__init__(self.table, alignment=alignment, margins=margins, style=style, *args, **kwargs)

    def fetch_data(self):
        """Fetch data from the provided function."""
        try:
            # Dynamically import the provider function
            module_name, function_name = self.data_provider.rsplit(".", 1)
            module = importlib.import_module(module_name)
            provider_function = getattr(module, function_name)
            data = provider_function()

            # Validate that data is a list of dictionaries
            if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                return data
            else:
                raise ValueError(f"Data provider must return a list of dictionaries, got {type(data)}")
        except (ImportError, AttributeError, ValueError) as e:
            print(f"Error fetching data from provider '{self.data_provider}': {e}")
            return []

    def populate_table(self, data):
        """Populate the table with data."""
        # Use specified columns or extract from data
        if self.columns:
            header_labels = self.columns
        else:
            header_labels = list(data[0].keys()) if data else []

        self.table.setColumnCount(len(header_labels))
        self.table.setHorizontalHeaderLabels(header_labels)
        self.table.setRowCount(len(data))

        for row_idx, row_data in enumerate(data):
            for col_idx, col_name in enumerate(header_labels):
                value = row_data.get(col_name, "")
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(value))

    def refresh_data(self):
        """Refresh the table data."""
        print("Refreshing table data...")
        data = self.fetch_data()
        self.populate_table(data)
