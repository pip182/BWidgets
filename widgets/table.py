from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QVBoxLayout
from PySide6.QtGui import QColor, QBrush
from widgets.base_widget import BaseWidget

class Table(BaseWidget):
    def __init__(
        self,
        data=None,
        columns=None,
        data_provider=None,
        interval=None,
        results_handler=None,
        alignment="center",
        margins=None,
        style=None,
        *args,
        **kwargs,
    ):
        """
        Create a Table widget.

        Args:
            data: Static list of rows for the table (optional).
            columns: List of columns to display (optional).
            data_provider: A string specifying a function to fetch dynamic data (optional).
            interval: Interval in milliseconds to refresh the data (optional).
            results_handler: A string specifying a function to process data (optional).
            alignment: Alignment of the widget.
            margins: Margins for the widget.
            style: CSS-like styles for the widget.
        """
        self.table = QTableWidget()
        self.columns = columns
        self.data_provider = data_provider
        self.interval = interval
        self.results_handler = results_handler
        self.style = style or {}

        # Initialize BaseWidget
        super().__init__(
            alignment=alignment,
            margins=margins,
            data_provider=data_provider,
            results_handler=results_handler,
            *args,
            **kwargs,
        )

        # Add loading label and table to the layout
        self.add_child_widget(self.table)

        self.show_loading()

        # Apply table styles
        self.apply_table_styles()

        # Adjust table settings
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Schedule initial data fetch
        if data_provider:
            self.fetch_data()  # Ensure asynchronous fetching
        elif data:
            self.populate_table(data)

        # Start refresh timer if interval is provided
        if interval and data_provider:
            self.timer = QTimer()
            self.timer.timeout.connect(self.fetch_data)
            self.timer.start(interval)

    def apply_table_styles(self):
        """Apply table-specific styles."""
        padding = self.style.get("padding", "0px")  # Default to no padding
        stylesheet = f"""
            QTableWidget::item {{
                padding: {padding};
            }}
        """
        self.table.setStyleSheet(stylesheet)

    def process_data(self, data):
        """Process the fetched data and populate the table."""
        if not isinstance(data, list):
            print("Expected data to be a list, but got:", type(data))
            return

        # Populate the table with processed data
        self.populate_table(data)
        self.show_table()

    def populate_table(self, data):
        """Populate the table with data."""
        # Ensure columns are a dictionary of key-value pairs
        header_mapping = self.columns.keys()
        header_labels = self.columns.values()

        # Configure table dimensions and headers
        self.table.setColumnCount(len(header_labels))
        self.table.setHorizontalHeaderLabels(header_labels)
        self.table.setRowCount(len(data))

        print("Populating table with data...", header_labels, len(data))

        # Populate the table using the key-value mapping
        for row_idx, row_data in enumerate(data):
            for col_idx, (data_key, column_header) in enumerate(self.columns.items()):
                # Match data_key with keys in row_data
                value = str(row_data.get(data_key, ""))
                item = QTableWidgetItem(value)
                print(f"Setting item at ({row_idx}, {col_idx}): {value}, header: {column_header}")
                self.apply_cell_style(item, column_header, value)
                self.table.setItem(row_idx, col_idx, item)

        # Trigger table redraw
        self.table.viewport().update()

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
        """
        Check if the value meets the condition.

        Supported conditions:
        - ">X" : Greater than X
        - "<X" : Less than X
        - ">=X" : Greater than or equal to X
        - "<=X" : Less than or equal to X
        - "==X" : Equal to X
        - "!=X" : Not equal to X
        """
        try:
            # Attempt to interpret value as a number if condition is numeric
            value = float(value) if isinstance(value, (int, float, str)) and value.isdigit() else value
        except ValueError:
            pass

        if isinstance(condition_value, str):
            # Handle comparison operators
            if condition_value.startswith(">="):
                return float(value) >= float(condition_value[2:])
            elif condition_value.startswith("<="):
                return float(value) <= float(condition_value[2:])
            elif condition_value.startswith(">"):
                return float(value) > float(condition_value[1:])
            elif condition_value.startswith("<"):
                return float(value) < float(condition_value[1:])
            elif condition_value.startswith("=="):
                return value == condition_value[2:]
            elif condition_value.startswith("!="):
                return value != condition_value[2:]

        # Exact match
        return value == condition_value

    def show_table(self):
        """Show the table and hide the loading indicator."""
        self.loading_label.hide()
        self.table.show()

    def show_loading(self):
        """Show the loading indicator and hide the table."""
        self.loading_label.show()
        self.table.hide()
