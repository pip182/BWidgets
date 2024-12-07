import sys
import yaml
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QWidget,
    QMenu,
    QSizePolicy
)
from widgets.label import Label
from widgets.button import Button
from widgets.dropdown import Dropdown
from widgets.input import Input
from widgets.latency_chart import LatencyChartWidget
from widgets.table import Table
from widgets.timer import TimerWidget


def apply_style(widget, style, debug=False):
    """Apply styling properties to a PySide6 widget."""
    css = [f"{key}: {value};" for key, value in style.items()]
    if debug:
        css.append("border: 3px solid green;")  # Debug border
    widget.setStyleSheet(" ".join(css))


def create_widget(widget_config, debug=False):
    """Create a widget dynamically based on its type."""
    widget_type = widget_config["type"]
    style = widget_config.get("style", {})
    alignment = widget_config.get("alignment", "center").lower()
    margins = widget_config.get("margins", [0, 0, 0, 0])  # Default to no margins

    if widget_type == "label":
        widget = Label(
            text=widget_config["text"],
            alignment=alignment,
            margins=margins,
            style=style
        )
    elif widget_type == "button":
        widget = Button(
            text=widget_config["text"],
            actions=widget_config["action"],
            alignment=alignment,
            margins=margins,
            style=style
        )
    elif widget_type == "dropdown":
        widget = Dropdown(
            options=widget_config["options"],
            actions=widget_config.get("action", []),
            alignment=alignment,
            margins=margins,
            style=style
        )
    elif widget_type == "input":
        widget = Input(
            placeholder=widget_config.get("placeholder", ""),
            alignment=alignment,
            margins=margins,
            style=style
        )
    elif widget_type == "latency_chart":
        widget = LatencyChartWidget(
            target_host=widget_config["target_host"],
            max_x=widget_config.get("max_points", 180),
            interval=widget_config.get("interval", 1000),
            irregular_factor=widget_config.get("irregular_factor", 3),
            alignment=alignment,
            margins=margins,
            style=style
        )
    elif widget_type == "table":
        widget = Table(
            data=widget_config.get("data", []),  # Fallback to empty list if no data is provided
            columns=widget_config.get("columns", None),
            data_provider=widget_config.get("data_provider", None),
            alignment=alignment,
            margins=margins,
            style=style
        )
    elif widget_type == "timer":
        widget = TimerWidget(
            duration=widget_config["duration"],
            alignment=alignment,
            margins=margins,
            style=style
        )
    else:
        raise ValueError(f"Unknown widget type: {widget_type}")

    return widget


def create_layout(layout_type, container_config):
    """Create a layout dynamically based on its type."""
    layout_map = {
        "vertical": QVBoxLayout,
        "horizontal": QHBoxLayout,
        "grid": QGridLayout
    }

    if layout_type not in layout_map:
        raise ValueError(f"Unsupported layout type: {layout_type}")

    layout = layout_map[layout_type]()

    # Apply container-level padding and margins
    padding = container_config.get("padding", [0, 0, 0, 0])  # Default to no padding
    margins = container_config.get("margins", [0, 0, 0, 0])  # Default to no margins

    layout.setContentsMargins(*margins)
    if not isinstance(layout, QGridLayout):
        layout.setSpacing(0)

    return layout, padding


def create_widget_container(container_config):
    """Create a container and populate it with widgets."""
    container = QWidget()
    layout_type = container_config.get("layout", "vertical")
    layout, padding = create_layout(layout_type, container_config)
    debug = container_config.get("debug", False)

    for widget_config in container_config["widgets"]:
        widget = create_widget(widget_config, debug=debug)

        if isinstance(layout, QGridLayout):
            # Handle grid-specific parameters
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

        # Handle frameless window
        self.is_frameless = container_config.get("frameless", False)
        self.toggle_frameless(self.is_frameless)

        # Handle z-order behavior
        z_order = container_config.get("z-order", None)
        if z_order == "always_above":
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        elif z_order == "always_below":
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnBottomHint)

        # Store container configuration
        self.container_config = container_config

        # Create and set the central widget container
        container = create_widget_container(container_config)
        self.setCentralWidget(container)

    def toggle_frameless(self, frameless):
        """Enable or disable frameless mode."""
        if frameless:
            self.setWindowFlags(Qt.FramelessWindowHint | self.windowFlags())
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.FramelessWindowHint)
        self.show()

    def mousePressEvent(self, event):
        """Handle right-click events to show the context menu."""
        if event.button() == Qt.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())

    def show_context_menu(self, position):
        """Show the context menu with the option to close or toggle frameless."""
        menu = QMenu(self)

        # Apply context menu style from the configuration
        context_menu_style = self.container_config.get("context_menu_style", {})
        item_style = context_menu_style.get("item_style", {})
        item_hover_style = context_menu_style.get("item_hover_style", {})

        if context_menu_style:
            css = [
                f"QMenu {{ {key}: {value}; }}" for key, value in context_menu_style.items() if key not in ["item_style", "item_hover_style"]
            ]
            if item_style:
                css.append(
                    f"QMenu::item {{ {'; '.join([f'{k}: {v}' for k, v in item_style.items()])}; }}"
                )
            if item_hover_style:
                css.append(
                    f"QMenu::item:selected {{ {'; '.join([f'{k}: {v}' for k, v in item_hover_style.items()])}; }}"
                )
            menu.setStyleSheet(" ".join(css))

        # Add actions to the context menu
        toggle_frameless_action = menu.addAction("Toggle Frameless")
        close_action = menu.addAction("Close")
        action = menu.exec(position)

        # Handle the selected action
        if action == toggle_frameless_action:
            self.is_frameless = not self.is_frameless
            self.toggle_frameless(self.is_frameless)
        elif action == close_action:
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
