import sys
import yaml
from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QMenu, QWidget

from widgets.label import Label
from widgets.button import Button
from widgets.dropdown import Dropdown
from widgets.input import Input
from widgets.table import Table
from widgets.latency_chart import LatencyChartWidget
from widgets.timer import TimerWidget

# Widget registry
widget_registry = {}


def register_widget(widget_type):
    """Decorator to register widget creation functions."""
    def decorator(func):
        widget_registry[widget_type] = func
        return func
    return decorator


@register_widget("label")
def create_label_widget(config):
    return Label(
        text=config.get("text", ""),
        interval=config.get("interval", None),
        alignment=config.get("alignment", "center"),
        data_provider=config.get("data_provider"),
        results_handler=config.get("results-handler"),
        style=config.get("style", {}),
    )


@register_widget("button")
def create_button_widget(config):
    return Button(
        text=config.get("text", ""),
        actions=config.get("action", []),
        alignment=config.get("alignment", "center"),
        data_provider=config.get("data_provider"),
        results_handler=config.get("results-handler"),
    )


@register_widget("dropdown")
def create_dropdown_widget(config):
    return Dropdown(
        options=config.get("options", []),
        actions=config.get("action", []),
        alignment=config.get("alignment", "center"),
        data_provider=config.get("data_provider"),
        results_handler=config.get("results-handler"),
    )


@register_widget("table")
def create_table_widget(config):
    return Table(
        data_provider=config.get("data_provider"),
        results_handler=config.get("results-handler"),
        columns=config.get("columns"),
        interval=config.get("interval", None),
        alignment=config.get("alignment", "center"),
        margins=config.get("margins", [0, 0, 0, 0]),
        style=config.get("style", {}),
    )


@register_widget("latency_chart")
def create_latency_chart_widget(config):
    return LatencyChartWidget(
        target_host=config.get("target_host"),
        interval=config.get("interval", 1000),
        max_x=config.get("max_points", 180),
        irregular_factor=config.get("irregular_factor", 3),
        results_handler=config.get("results-handler"),
        data_provider=config.get("data_provider"),
        alignment=config.get("alignment", "center"),
        margins=config.get("margins", [0, 0, 0, 0]),
        style=config.get("style", {}),
    )


@register_widget("timer")
def create_timer_widget(config):
    return TimerWidget(
        duration=config.get("duration"),
        alignment=config.get("alignment", "center"),
        data_provider=config.get("data_provider"),
        results_handler=config.get("results-handler"),
    )


def create_widget(widget_config):
    """Create a widget dynamically using the registry."""
    widget_type = widget_config["type"]
    widget_name = widget_config.get("name", "")
    if widget_type in widget_registry:
        widget = widget_registry[widget_type](widget_config)
        widget.widget_type = widget_type
        widget.widget_name = widget_name
        return widget
    else:
        raise ValueError(f"Unknown widget type: {widget_type}")


def create_widget_container(container_config, thread_pool):
    """Create a widget container dynamically."""
    container = QWidget()
    layout_type = container_config.get("layout", "vertical")
    layout = create_layout(layout_type)

    for widget_config in container_config.get("widgets", []):
        widget_config["thread_pool"] = thread_pool
        widget = create_widget(widget_config)
        layout.addWidget(widget)
    container.setLayout(layout)

    return container


def create_layout(layout_type):
    """Create a layout based on the specified type."""
    from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout

    layout_map = {
        "vertical": QVBoxLayout,
        "horizontal": QHBoxLayout,
        "grid": QGridLayout,
    }
    if layout_type not in layout_map:
        raise ValueError(f"Unsupported layout type: {layout_type}")
    return layout_map[layout_type]()


class WidgetApp(QMainWindow):
    def __init__(self, title, geometry, container_config):
        super().__init__()
        self.setWindowTitle(title)
        self.setGeometry(*geometry)

        self.is_frameless = container_config.get("frameless", False)
        self.toggle_frameless(self.is_frameless)

        z_order = container_config.get("z-order", None)
        if z_order == "always_above":
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        elif z_order == "always_below":
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnBottomHint)

        self.container_config = container_config

        # Create a thread pool for this WidgetApp
        self.thread_pool = QThreadPool()

        container = create_widget_container(container_config, self.thread_pool)
        self.container = container
        self.setCentralWidget(container)

        self.setup_context_menu()

    def closeEvent(self, event):
        """Handle cleanup when the window is closed."""
        self.thread_pool.clear()
        self.thread_pool.waitForDone()
        super().closeEvent(event)

    def toggle_frameless(self, frameless):
        """Toggle window decoration."""
        self.is_frameless = frameless
        if self.is_frameless:
            self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags())
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.FramelessWindowHint)
        self.show()

    def setup_context_menu(self):
        """Set up a right-click context menu."""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        """Display the context menu."""
        menu = QMenu(self)
        toggle_decorations_action = menu.addAction("Toggle Decorations")
        close_window_action = menu.addAction("Close Window")

        action = menu.exec_(self.mapToGlobal(pos))
        if action == toggle_decorations_action:
            self.toggle_frameless(not self.is_frameless)
        elif action == close_window_action:
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load the configuration from config.yaml
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    # Create a window for each widget container
    windows = []
    for container_name, container_config in config.items():
        if container_name == "user_config":
            continue

        # Get title and geometry for the window
        title = container_config.get("title", container_name)
        geometry = container_config.get("geometry", [100, 100, 800, 600])

        # Create the window
        window = WidgetApp(title, geometry, container_config)
        window.show()
        windows.append(window)

    sys.exit(app.exec())
