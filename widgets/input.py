from PySide6.QtWidgets import QLineEdit
from widgets.base_widget import BaseWidget


class Input(BaseWidget):
    def __init__(self, placeholder="", alignment="center", margins=None, style=None, *args, **kwargs):
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(placeholder)

        super().__init__(self.input_field, alignment=alignment, margins=margins, style=style, *args, **kwargs)

    def get_text(self):
        return self.input_field.text()
