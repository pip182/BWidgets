from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtGui import QColor, QBrush
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
        self.style = style or {}

        # Fetch data from the provider if specified
        if data_provider:
            data = self.fetch_data()

        # Populate the table
        if data:
            self.populate_table(data)

        # Apply styles including padding
        self.apply_table_styles()

        # Adjust table settings
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Apply header alignment if specified
        header_style = self.style.get("header_style", {})
        if "alignment" in header_style:
            alignment = self.parse_alignment(header_style["alignment"])
            self.table.horizontalHeader().setDefaultAlignment(alignment)

        # Start refresh timer if interval is provided
        if refresh_interval and data_provider:
            print(f"Starting data refresh timer with interval {refresh_interval} ms")
            self.timer = QTimer()
            self.timer.timeout.connect(self.refresh_data)
            self.timer.start(refresh_interval)

        super().__init__(self.table, alignment=alignment, margins=margins, style=style, *args, **kwargs)

    def apply_table_styles(self):
        """Apply table-specific styles including cell padding."""
        padding = self.style.get("padding", "0px")  # Default to no padding
        stylesheet = f"""
            QTableWidget::item {{
                padding: {padding};
            }}
        """
        self.table.setStyleSheet(stylesheet)

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
                item = QTableWidgetItem(value)
                self.apply_cell_style(item, col_name, value)
                self.table.setItem(row_idx, col_idx, item)

    def refresh_data(self):
        """Refresh the table data."""
        print("Refreshing table data...")
        data = self.fetch_data()
        self.populate_table(data)

    def apply_cell_style(self, item, column, value):
        """Apply styles to a table cell."""
        cell_style = self.style.get("cell_style", {})
        default_style = cell_style.get("default", {})
        conditions = cell_style.get("conditions", [])

        # Apply default styles
        if "background-color" in default_style:
            item.setBackground(QBrush(QColor(default_style["background-color"])))
        if "color" in default_style:
            item.setForeground(QBrush(QColor(default_style["color"])))
        if "alignment" in default_style:
            alignment = self.parse_alignment(default_style["alignment"])
            item.setTextAlignment(alignment)

        # Apply conditional styles
        for condition in conditions:
            if condition.get("column") == column:
                condition_value = condition.get("value", None)
                if self.meets_condition(value, condition_value):
                    if "background-color" in condition:
                        item.setBackground(QBrush(QColor(condition["background-color"])))
                    if "color" in condition:
                        item.setForeground(QBrush(QColor(condition["color"])))

    def meets_condition(self, value, condition_value):
        """Check if the value meets the condition."""
        if isinstance(condition_value, str) and condition_value.startswith(">"):
            try:
                return float(value) > float(condition_value[1:])
            except ValueError:
                return False
        elif value == condition_value:
            return True
        return False
