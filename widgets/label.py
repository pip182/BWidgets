
from PySide6.QtWidgets import QLabel
from widgets.base_widget import BaseWidget


class Label(BaseWidget):
    """Widget for displaying text labels."""

    def __init__(self, text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = QLabel(text, self)
