from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt


class BaseWidget(QWidget):
    """Base widget class that provides alignment, layout, and styling."""

    def __init__(self, content_widget=None, alignment="center", margins=None, style=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Default to no margins if not provided
        margins = margins or [0, 0, 0, 0]
        self.layout.setContentsMargins(*margins)

        # Set alignment
        self.layout.setAlignment(self.parse_alignment(alignment))

        # Add the content widget if provided
        if content_widget:
            self.layout.addWidget(content_widget)

        # Apply styles if provided
        if style:
            self.apply_style(style)

    def apply_style(self, style):
        """Apply CSS-like styling to the widget."""
        css = [f"{key}: {value};" for key, value in style.items()]
        self.setStyleSheet(" ".join(css))

    @staticmethod
    def parse_alignment(alignment_str):
        """Parse alignment string into Qt alignment flag."""
        alignment_map = {
            "left": Qt.AlignLeft,
            "right": Qt.AlignRight,
            "center": Qt.AlignCenter,
            "top": Qt.AlignTop,
            "bottom": Qt.AlignBottom
        }
        return alignment_map.get(alignment_str.lower(), Qt.AlignCenter)
