
from PySide6.QtWidgets import QComboBox
from widgets.base_widget import BaseWidget


class Dropdown(BaseWidget):
    def __init__(self, options, actions=None, alignment="center", margins=None, style=None, *args, **kwargs):
        self.dropdown = QComboBox()
        self.dropdown.addItems(options)

        # Add dropdown actions
        if actions:
            self.dropdown.currentIndexChanged.connect(self.execute_actions)

        self.actions = actions
        super().__init__(self.dropdown, alignment=alignment, margins=margins, style=style, *args, **kwargs)

    def execute_actions(self, index):
        if self.actions:
            for action in self.actions:
                if action["type"] == "notification":
                    print(action.get("message", f"Selected index: {index}"))

    def on_selection(self):
        """Trigger actions when an option is selected."""
        selected = self.dropdown.currentText()
        for action in self.actions:
            if action["type"] == "python" and "function" in action:
                globals()[action["function"]](selected)
