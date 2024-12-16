from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer
import importlib
import inspect
import ast


def resolve_callable_from_string(provider_string):
    """Parse and resolve a string into a callable and its arguments."""
    if "(" in provider_string and provider_string.endswith(")"):
        module_function, args_str = provider_string.split("(", 1)
        module_name, function_name = module_function.rsplit(".", 1)
        module = importlib.import_module(module_name)
        function = getattr(module, function_name)
        args_str = args_str.rstrip(")")
        args = ast.literal_eval(f"({args_str},)") if args_str.strip() else tuple()
        return function, args
    else:
        module_name, function_name = provider_string.rsplit(".", 1)
        module = importlib.import_module(module_name)
        function = getattr(module, function_name)
        return function, tuple()


class BaseWidget(QWidget):
    ALIGNMENT_MAP = {
        "center": Qt.AlignCenter,
        "left": Qt.AlignLeft,
        "right": Qt.AlignRight,
        "top": Qt.AlignTop,
        "bottom": Qt.AlignBottom,
    }

    def __init__(
        self,
        alignment="center",
        margins=None,
        data_provider=None,
        results_handler=None,
        interval=None,
        text=None,
        widget_type=None,
        widget_name=None,
        *args,
        **kwargs
    ):
        """
        Base class for widgets with alignment, data fetching, and periodic updates.

        Args:
            alignment (str): Alignment for the widget.
            margins (list): Margins for the widget layout.
            data_provider (str): String specifying the data-fetching function.
            results_handler (str): String specifying the results handler function.
            interval (int): Interval for periodic updates (optional).
            text (str): Fallback text if no data provider is set.
            widget_type (str): Type of the widget (e.g., "label").
            widget_name (str): Optional name of the widget.
        """
        super().__init__(*args, **kwargs)
        self.data_provider = data_provider or text
        self.results_handler = results_handler
        self.interval = interval
        self.alignment = self.parse_alignment(alignment)
        self.widget_type = widget_type or "unknown"
        self.widget_name = widget_name

        if margins:
            self.setContentsMargins(*margins)

        # Initialize layout
        self.layout = QVBoxLayout()
        self.layout.setAlignment(self.alignment)
        self.setLayout(self.layout)

        # Add a loading indicator
        self.loading_label = QLabel("Loading...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.loading_label)
        self.hide_loading()

        # Timer for periodic updates
        self.timer = None
        if self.interval:
            self.start_periodic_updates()

        # Start fetching data in the background
        self.defer_data_fetching()

    @staticmethod
    def parse_alignment(alignment_str):
        """Parse alignment string into Qt alignment constant."""
        return BaseWidget.ALIGNMENT_MAP.get(alignment_str.lower(), Qt.AlignCenter)

    def add_child_widget(self, widget):
        """Add a child widget to the layout."""
        self.layout.addWidget(widget)

    def fetch_data(self):
        """Fetch data using the data provider."""
        if not self.data_provider:
            self.log("No data provider configured.")
            return None

        try:
            function, args = resolve_callable_from_string(self.data_provider)
            if inspect.iscoroutinefunction(function):
                self.log("Data provider is asynchronous. Use async methods.")
                return None
            else:
                return function(*args)
        except Exception as e:
            self.log(f"Error fetching data: {e}")
            return None

    def handle_results(self, data):
        """Process fetched data using the results handler."""
        if not self.results_handler:
            return data

        try:
            function, args = resolve_callable_from_string(self.results_handler)
            return function(data, *args)
        except Exception as e:
            self.log(f"Error processing results: {e}")
            return data

    def defer_data_fetching(self):
        """Defer data fetching to ensure UI renders immediately."""
        def fetch_and_process():
            self.show_loading()
            data = self.fetch_data()
            if data is not None:
                processed_data = self.handle_results(data)
                self.on_data_fetched(processed_data)
            self.hide_loading()

        QTimer.singleShot(0, fetch_and_process)

    def start_periodic_updates(self):
        """Start periodic updates for the widget."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.periodic_task)
        self.timer.start(self.interval)

    def periodic_task(self):
        """Fetch and process data periodically."""
        self.log("Running periodic task.")
        self.defer_data_fetching()

    def on_data_fetched(self, data):
        """Callback when data is fetched and processed."""
        self.log(f"Data fetched: {data}")
        # Override in subclasses to handle fetched data

    def show_loading(self):
        """Display the loading indicator."""
        if self.data_provider:
            self.loading_label.show()

    def hide_loading(self):
        """Hide the loading indicator."""
        self.loading_label.hide()

    def log(self, message):
        """Log a message with widget context."""
        widget_info = f"[WidgetType: {self.widget_type}"
        if self.widget_name:
            widget_info += f", WidgetName: {self.widget_name}"
        widget_info += "]"
        print(f"{widget_info} {message}")
