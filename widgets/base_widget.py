
from PySide6.QtWidgets import QWidget


class BaseWidget(QWidget):
    """Base class for all widgets."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
