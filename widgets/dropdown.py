
from PySide6.QtWidgets import QComboBox
from widgets.base_widget import BaseWidget


class Dropdown(BaseWidget):
    """Dropdown widget for selections."""

    def __init__(self, options, actions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dropdown = QComboBox(self)
        self.dropdown.addItems(options)
        self.dropdown.currentIndexChanged.connect(self.on_selection)
        self.actions = actions

    def on_selection(self):
        """Trigger actions when an option is selected."""
        selected = self.dropdown.currentText()
        for action in self.actions:
            if action["type"] == "python" and "function" in action:
                globals()[action["function"]](selected)
