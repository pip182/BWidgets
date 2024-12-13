from PySide6.QtWidgets import QLabel
from widgets.base_widget import BaseWidget


class Label(BaseWidget):
    def __init__(self, text="", alignment="center", data_provider=None, results_handler=None, *args, **kwargs):
        super().__init__(data_provider=data_provider, results_handler=results_handler, *args, **kwargs)
        self.label = QLabel(text)
        self.update_content()

    def update_content(self):
        """Update the label content dynamically."""
        data = self.fetch_data()
        if data is not None:
            data = self.handle_results(data)
            self.label.setText(str(data))
