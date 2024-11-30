
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from widgets.base_widget import BaseWidget


class Table(BaseWidget):
    """Table widget for displaying tabular data."""

    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table = QTableWidget(len(data), len(data[0]), self)
        for i, row in enumerate(data):
            for j, cell in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(cell))
