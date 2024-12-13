from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
import importlib


class BaseWidget(QWidget):
    ALIGNMENT_MAP = {
        "center": Qt.AlignCenter,
        "left": Qt.AlignLeft,
        "right": Qt.AlignRight,
        "top": Qt.AlignTop,
        "bottom": Qt.AlignBottom,
    }

    def __init__(self, alignment="center", data_provider=None, results_handler=None, *args, **kwargs):
        """
        Base class for widgets with support for data providers, result handlers, and alignment.

        Args:
            alignment: String representing widget alignment ("center", "left", etc.).
            data_provider: String specifying the function or method to fetch dynamic data.
            results_handler: String specifying the function to process data.
        """
        super().__init__(*args, **kwargs)
        self.data_provider = data_provider
        self.results_handler = results_handler
        self.alignment = self.parse_alignment(alignment)

    @staticmethod
    def parse_alignment(alignment_str):
        """Parse alignment string into Qt alignment constant."""
        return BaseWidget.ALIGNMENT_MAP.get(alignment_str.lower(), Qt.AlignCenter)

    def fetch_data(self):
        """Fetch data using the data_provider."""
        if not self.data_provider:
            return None

        try:
            # Dynamically import the provider function
            module_name, function_name = self.data_provider.rsplit(".", 1)
            module = importlib.import_module(module_name)
            provider_function = getattr(module, function_name)
            data = provider_function()
            return data
        except (ImportError, AttributeError, ValueError) as e:
            print(f"Error fetching data from provider '{self.data_provider}': {e}")
            return None

    def handle_results(self, data):
        """Process data using the results_handler."""
        if not self.results_handler:
            return data

        try:
            # Dynamically import the handler function
            module_name, function_name = self.results_handler.rsplit(".", 1)
            module = importlib.import_module(module_name)
            handler_function = getattr(module, function_name)
            return handler_function(data)
        except (ImportError, AttributeError, ValueError) as e:
            print(f"Error processing results with handler '{self.results_handler}': {e}")
            return data
