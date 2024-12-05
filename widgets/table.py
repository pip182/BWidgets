from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from widgets.base_widget import BaseWidget


class Table(BaseWidget):
    def __init__(self, data, alignment="center", margins=None, style=None, *args, **kwargs):
        self.table = QTableWidget(len(data), len(data[0]))
        self.table.setHorizontalHeaderLabels(data[0])

        for row_idx, row_data in enumerate(data[1:], start=1):
            for col_idx, cell_data in enumerate(row_data):
                self.table.setItem(row_idx - 1, col_idx, QTableWidgetItem(cell_data))

        super().__init__(self.table, alignment=alignment, margins=margins, style=style, *args, **kwargs)
