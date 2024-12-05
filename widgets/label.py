from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel
from widgets.base_widget import BaseWidget


class Label(BaseWidget):
    def __init__(self, text, alignment="center", margins=None, style=None, *args, **kwargs):
        # Map alignment strings to Qt alignment flags
        alignment_map = {
            "center": Qt.AlignCenter,
            "left": Qt.AlignLeft,
            "right": Qt.AlignRight,
            "top": Qt.AlignTop,
            "bottom": Qt.AlignBottom,
        }
        alignment_flag = alignment_map.get(alignment, Qt.AlignCenter)

        # Create the QLabel with correct alignment
        content_widget = QLabel(text)
        content_widget.setAlignment(alignment_flag)

        # Initialize BaseWidget
        super().__init__(content_widget, alignment=alignment, margins=margins, style=style, *args, **kwargs)
