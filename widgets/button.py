from PySide6.QtWidgets import QPushButton
from widgets.base_widget import BaseWidget


class Button(BaseWidget):
    def __init__(self, text="", actions=None, data_provider=None, results_handler=None, *args, **kwargs):
        super().__init__(data_provider=data_provider, results_handler=results_handler, *args, **kwargs)
        self.button = QPushButton(text)
        self.actions = actions or []
        self.update_content()

        self.button.clicked.connect(self.on_click)

    def on_click(self):
        """Execute actions when the button is clicked."""
        for action in self.actions:
            print(f"Executing action: {action}")

    def update_content(self):
        """Update the button text dynamically."""
        data = self.fetch_data()
        if data is not None:
            data = self.handle_results(data)
            self.button.setText(str(data))
