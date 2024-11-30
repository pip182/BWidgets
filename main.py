
import sys
import json
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget
from widgets.latency_chart import LatencyChartWidget
from widgets.label import Label
from widgets.button import Button
from widgets.timer import TimerWidget
from widgets.table import Table
from widgets.dropdown import Dropdown


def apply_style(widget, style):
    """Apply styling properties to a PySide6 widget."""
    css = [f"{key}: {value};" for key, value in style.items()]
    widget.setStyleSheet(" ".join(css))


def create_widget(widget_config):
    """Create a widget dynamically based on its type."""
    widget_type = widget_config["type"]
    style = widget_config.get("style", {})
    size = widget_config.get("size", {"width": 200, "height": 100})

    if widget_type == "label":
        widget = Label(widget_config["text"])
    elif widget_type == "latency_chart":
        widget = LatencyChartWidget(
            target_host=widget_config["target_host"],
            max_x=widget_config.get("max_points", 180),
            interval=widget_config.get("interval", 1000),
            irregular_factor=widget_config.get("irregular_factor", 3)
        )
    elif widget_type == "button":
        widget = Button(
            text=widget_config["text"],
            actions=widget_config["action"]
        )
    elif widget_type == "timer":
        widget = TimerWidget(
            duration=widget_config["duration"],
            title=widget_config.get("title", "Timer")
        )
    elif widget_type == "table":
        widget = Table(data=widget_config["data"])
    elif widget_type == "dropdown":
        widget = Dropdown(
            options=widget_config["options"],
            actions=widget_config.get("action", [])
        )
    else:
        raise ValueError(f"Unknown widget type: {widget_type}")

    # Apply size and style
    widget.setFixedSize(size["width"], size["height"])
    apply_style(widget, style)
    return widget


def create_layout(layout_type):
    """Create a layout dynamically based on its type."""
    if layout_type == "QVBoxLayout":
        return QVBoxLayout()
    elif layout_type == "QHBoxLayout":
        return QHBoxLayout()
    elif layout_type == "QGridLayout":
        return QGridLayout()
    else:
        raise ValueError(f"Unsupported layout type: {layout_type}")


def create_widget_container(container_config):
    """Create a container and populate it with widgets."""
    container = QWidget()
    layout_type = container_config.get("layout", "QVBoxLayout")
    layout = create_layout(layout_type)

    for widget_config in container_config["widgets"]:
        widget = create_widget(widget_config)

        if isinstance(layout, QGridLayout):
            # Handle grid-specific parameters
            row = widget_config.get("row", 0)
            column = widget_config.get("column", 0)
            layout.addWidget(widget, row, column)
        else:
            layout.addWidget(widget)

    container.setLayout(layout)
    return container


class WidgetApp(QMainWindow):
    """Main application window for a widget container."""
    def __init__(self, title, geometry, container_config):
        super().__init__()
        self.setWindowTitle(title)
        self.setGeometry(*geometry)

        container = create_widget_container(container_config)
        self.setCentralWidget(container)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load the configuration
    with open("widgets_config.json", "r") as f:
        config = json.load(f)

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
