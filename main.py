import sys
import yaml
import subprocess
import importlib
import asyncio
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QWidget,
    QMenu,
)
from widgets.label import Label
from widgets.button import Button
from widgets.dropdown import Dropdown
from widgets.input import Input
from widgets.table import Table
from widgets.timer import TimerWidget
from widgets.latency_chart import LatencyChartWidget


async def fetch_data_from_provider(provider):
    """
    Fetch data from a provider which could be a Python class, method, or shell command.

    Args:
        provider (str | callable): Provider definition as string or callable.

    Returns:
        Any: Result of the data provider or handler execution.
    """
    if callable(provider):
        if asyncio.iscoroutinefunction(provider):
            return await provider()
        return provider()

    if isinstance(provider, str):
        if provider.startswith("!"):
            # Handle shell commands asynchronously
            command = provider[1:].strip()
            try:
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await process.communicate()
                if process.returncode == 0:
                    return stdout.decode().strip()
                else:
                    print(f"Error executing shell command '{command}': {stderr.decode().strip()}")
                    return None
            except Exception as e:
                print(f"Error executing shell command '{command}': {e}")
                return None
        else:
            # Handle Python class or function references
            try:
                module_name, call_expr = provider.split("(", 1)
                module_name, class_name = module_name.rsplit(".", 1)
                args = call_expr.rstrip(")")

                module = importlib.import_module(module_name)
                klass = getattr(module, class_name)

                if args:
                    instance = eval(f"klass({args})")
                else:
                    instance = klass()

                if callable(instance):
                    if asyncio.iscoroutinefunction(instance):
                        return await instance()
                    return instance()
                return instance
            except (ImportError, AttributeError, SyntaxError) as e:
                print(f"Error processing provider '{provider}': {e}")
                return None

    print(f"Unsupported provider type: {type(provider)}")
    return None


async def create_widget(widget_config, debug=False):
    """Create a widget dynamically and set up data handling."""
    widget = None
    widget_type = widget_config["type"]
    style = widget_config.get("style", {})
    alignment = widget_config.get("alignment", "center").lower()
    margins = widget_config.get("margins", [0, 0, 0, 0])
    data_provider = widget_config.get("data_provider", None)
    results_handler = widget_config.get("results-handler", None)

    if widget_type == "label":
        widget = Label(
            text=widget_config.get("text", ""),
            alignment=alignment,
            data_provider=data_provider,
            results_handler=results_handler,
        )
    elif widget_type == "button":
        widget = Button(
            text=widget_config.get("text", ""),
            actions=widget_config.get("action", []),
            alignment=alignment,
            data_provider=data_provider,
            results_handler=results_handler,
        )
    elif widget_type == "dropdown":
        widget = Dropdown(
            options=widget_config.get("options", []),
            actions=widget_config.get("action", []),
            alignment=alignment,
            data_provider=data_provider,
            results_handler=results_handler,
        )
    elif widget_type == "table":
        widget = Table(
            data_provider=data_provider,
            results_handler=results_handler,
            alignment=alignment,
            columns=widget_config.get("columns"),
            refresh_interval=widget_config.get("refresh_interval", None),
        )
    elif widget_type == "input":
        widget = Input(
            placeholder=widget_config.get("placeholder", ""),
            alignment=alignment,
            data_provider=data_provider,
            results_handler=results_handler,
        )
    elif widget_type == "timer":
        widget = TimerWidget(
            duration=widget_config["duration"],
            alignment=alignment,
            data_provider=data_provider,
            results_handler=results_handler,
        )
    elif widget_type == "latency_chart":
        widget = LatencyChartWidget(
            alignment=alignment,
            interval=widget_config.get("interval", 1000),
            irregular_factor=widget_config.get("irregular_factor", 3),
            margins=margins,
            max_x=widget_config.get("max_points", 180),
            refresh_interval=widget_config.get("refresh_interval", None),
            results_handler=results_handler,
            style=style,
            target_host=widget_config["target_host"],
        )
    else:
        raise ValueError(f"Unknown widget type: {widget_type}")

    return widget


def create_layout(layout_type, container_config):
    """Create a layout dynamically based on its type."""
    layout_map = {
        "vertical": QVBoxLayout,
        "horizontal": QHBoxLayout,
        "grid": QGridLayout,
    }

    if layout_type not in layout_map:
        raise ValueError(f"Unsupported layout type: {layout_type}")

    layout = layout_map[layout_type]()
    padding = container_config.get("padding", [0, 0, 0, 0])
    margins = container_config.get("margins", [0, 0, 0, 0])

    layout.setContentsMargins(*margins)
    if not isinstance(layout, QGridLayout):
        layout.setSpacing(0)

    return layout, padding


async def create_widget_container(container_config):
    """Create a container and populate it with widgets."""
    container = QWidget()
    layout_type = container_config.get("layout", "vertical")
    layout, padding = create_layout(layout_type, container_config)
    debug = container_config.get("debug", False)

    for widget_config in container_config["widgets"]:
        widget = await create_widget(widget_config, debug=debug)

        if isinstance(layout, QGridLayout):
            row = widget_config.get("row", 0)
            column = widget_config.get("column", 0)
            layout.addWidget(widget, row, column)
        else:
            layout.addWidget(widget)

    container.setLayout(layout)
    container.setContentsMargins(*padding)
    return container


class WidgetApp(QMainWindow):
    """Main application window for a widget container."""

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

        container = asyncio.run(create_widget_container(container_config))
        self.setCentralWidget(container)

    def toggle_frameless(self, frameless):
        """Toggle window decoration."""
        self.is_frameless = frameless
        if self.is_frameless:
            self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags())
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.FramelessWindowHint)
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    windows = []
    for container_name, container_config in config.items():
        if container_name == "user_config":
            continue

        title = container_config.get("title", container_name)
        geometry = container_config.get("geometry", [100, 100, 800, 600])

        window = WidgetApp(title, geometry, container_config)
        window.show()
        windows.append(window)

    sys.exit(app.exec())
