from PySide6.QtWidgets import QPushButton
from widgets.base_widget import BaseWidget


class Button(BaseWidget):
    def __init__(self, text, actions, alignment="center", margins=None, style=None, *args, **kwargs):
        self.button = QPushButton(text)
        self.button.clicked.connect(self.execute_actions)
        self.actions = actions

        super().__init__(self.button, alignment=alignment, margins=margins, style=style, *args, **kwargs)

    def execute_actions(self):
        for action in self.actions:
            if action["type"] == "notification":
                print(action.get("message", "Button clicked!"))
