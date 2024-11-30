
from PySide6.QtWidgets import QPushButton
from widgets.base_widget import BaseWidget
from actions import send_notification


class Button(BaseWidget):
    """Interactive button widget."""

    def __init__(self, text, actions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.button = QPushButton(text, self)
        self.button.clicked.connect(self.execute_actions)
        self.actions = actions

    def execute_actions(self):
        """Execute all actions bound to the button."""
        for action in self.actions:
            if action["type"] == "python":
                if "function" in action:
                    globals()[action["function"]]()  # Call Python function
            elif action["type"] == "notification":
                send_notification(action.get("message", "Button clicked!"))
