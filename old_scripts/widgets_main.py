import sys
import json
import subprocess
from PySide6.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox
from PySide6.QtCore import Qt, QRunnable, QThreadPool, Signal, QObject
from PySide6 import QtGui


# Signal class to handle results in the main thread
class WorkerSignals(QObject):
    result = Signal(str)


# QRunnable Task Class for handling actions
class ActionTask(QRunnable):
    def __init__(self, action, function_map, target_widget=None):
        super().__init__()
        self.action = action
        self.function_map = function_map
        self.target_widget = target_widget
        self.signals = WorkerSignals()

    def run(self):
        result = self.execute_action(self.action)
        self.signals.result.emit(result)

    def execute_action(self, action):
        action_type = action.get("type")
        if action_type == "shell":
            command = action.get("command")
            return self.run_shell_command(command)
        elif action_type == "python":
            function_name = action.get("function")
            return self.run_python_function(function_name)

    def run_shell_command(self, command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.stdout.strip()
        except Exception as e:
            return f"Error executing shell command: {e}"

    def run_python_function(self, function_name):
        if function_name in self.function_map:
            try:
                return self.function_map[function_name]()
            except Exception as e:
                return f"Error executing function {function_name}: {e}"
        else:
            return f"Function {function_name} not found."


# Main Window Class
class CustomWidgetApp(QWidget):
    def __init__(self, config_file):
        super().__init__()
        self.setWindowTitle("Custom Widgets App with Inputs and Dropdowns")
        self.setGeometry(100, 100, 800, 600)

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Mapping of available functions that can be triggered from JSON
        self.function_map = {
            "greet_user": self.greet_user,
            "post_action_message": self.post_action_message
        }

        self.threadpool = QThreadPool()
        self.widgets = {}
        self.container_count = 0
        self.load_widgets(config_file)

    def load_widgets(self, config_file):
        try:
            with open(config_file, 'r') as file:
                widget_configs = json.load(file)

            for widget_conf in widget_configs:
                widget_type = widget_conf.get("type")
                position = widget_conf.get("position", [0, 0])
                size = widget_conf.get("size", [100, 50])
                style = widget_conf.get("style", {})

                if widget_type == "widgetContainer":
                    self.create_container(widget_conf, position, size, style)
                else:
                    self.create_widget(self, widget_conf)

        except Exception as e:
            print(f"Error loading configuration: {e}")

    def create_container(self, config, position, size, style):
        container = QWidget(self)
        container.setGeometry(position[0], position[1], size[0], size[1])
        self.apply_style(container, style)

        layout = QVBoxLayout(container)

        title_conf = config.get("title")
        if title_conf:
            title_text = title_conf.get("text", "Container")
            title_style = title_conf.get("style", {})
            self.add_container_title(container, layout, title_text, title_style)

        if config.get("closable", False):
            close_button_conf = config.get("closeButton", {})
            self.add_close_button(container, close_button_conf)

        self.container_count += 1

        container.show()

        for widget_conf in config.get("widgets", []):
            self.create_widget(container, widget_conf)

    def add_container_title(self, container, layout, title_text, style):
        title_label = QLabel(title_text, container)
        self.apply_style(title_label, style)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(title_label)

    def add_close_button(self, container, close_button_conf):
        close_position = close_button_conf.get("position", [350, 10])
        close_text = close_button_conf.get("text", "Close")
        close_style = close_button_conf.get("style", {})

        close_button = QPushButton(close_text, container)
        close_button.setGeometry(close_position[0], close_position[1], 50, 30)
        self.apply_style(close_button, close_style)

        close_button.clicked.connect(lambda: self.close_container(container))

    def close_container(self, container):
        container.hide()
        self.container_count -= 1
        if self.container_count == 0:
            self.close()

    def create_widget(self, parent, widget_conf):
        widget_type = widget_conf.get("type")
        position = widget_conf.get("position", [0, 0])
        size = widget_conf.get("size", [100, 50])
        style = widget_conf.get("style", {})
        widget_id = widget_conf.get("id", None)

        # Handle Label, Button, Table, Input, and Dropdown widgets
        if widget_type == "label":
            self.create_label(parent, widget_conf.get("text", ""), position, size, style, widget_id)
        elif widget_type == "button":
            actions = widget_conf.get("action", [])
            self.create_button(parent, widget_conf.get("text", ""), position, size, actions, style)
        elif widget_type == "table":
            columns = widget_conf.get("columns", [])
            self.create_table(parent, widget_id, position, size, columns, style)
        elif widget_type == "input":
            self.create_input(parent, position, size, widget_conf.get("placeholder", ""), style, widget_id)
        elif widget_type == "dropdown":
            options = widget_conf.get("options", [])
            self.create_dropdown(parent, options, position, size, style, widget_id)

    def create_label(self, parent, text, position, size, style, widget_id=None):
        label = QLabel(text, parent)
        label.setGeometry(position[0], position[1], size[0], size[1])
        label.setAlignment(Qt.AlignCenter)
        self.apply_style(label, style)
        if widget_id:
            self.widgets[widget_id] = label

    def create_button(self, parent, text, position, size, actions, style):
        button = QPushButton(text, parent)
        button.setGeometry(position[0], position[1], size[0], size[1])
        self.apply_style(button, style)
        button.clicked.connect(lambda: self.handle_actions(actions))

    def create_table(self, parent, widget_id, position, size, columns, style):
        table = QTableWidget(parent)
        table.setGeometry(position[0], position[1], size[0], size[1])
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)

        # Set custom cell styles via 'cellStyle' property
        cell_style_config = style.get("cell", {
            "background-color": "#333333",
            "color": "#FFFFFF",
            "font-size": 12,
            "alignment": Qt.AlignCenter
        })
        table.setProperty("cellStyle", cell_style_config)

        header_style_config = style.get("header", {
            "background-color": "#444444",
            "color": "#FFFFFF",
            "font-size": 16
        })
        table.setProperty("headerStyle", header_style_config)

        header = table.horizontalHeader()
        self.apply_style(header, header_style_config)

        table_style_config = style.get("table", {})

        # Apply scrollbar styles
        scrollbar_style_config = style.get("scrollbar", {
            "width": "12px",
            "background-color": "#2E2E2E",
            "handle-color": "#CCCCCC"
        })

        scrollbar_config_string = f"""
            QScrollBar::vertical {{
                width: {scrollbar_style_config.get('width', '12px')};
                background-color: {scrollbar_style_config.get('background-color', '#2E2E2E')};
                border: {scrollbar_style_config.get('border', '1px solid #333333')};
            }}
            QScrollBar::handle:vertical {{
                width: {scrollbar_style_config.get('width', '12px')};
                background-color: {scrollbar_style_config.get('handle-color', '#CCCCCC')};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
            QScrollbar::horizontal {{
                width: {scrollbar_style_config.get('width', '12px')};
                background-color: {scrollbar_style_config.get('background-color', '#2E2E2E')};
                border: {scrollbar_style_config.get('border', '1px solid #333333')};
            }}
            QScrollBar::handle:horizontal {{
                width: {scrollbar_style_config.get('width', '12px')};
                background-color: {scrollbar_style_config.get('handle-color', '#CCCCCC')};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                border: none;
                background: none;
            }}
        """

        # Apply the table-wide styles (background color, borders, etc.)
        self.apply_style(table, table_style_config, scrollbar_config_string)

        # Populate the table
        self.populate_table('', table)

        if widget_id:
            self.widgets[widget_id] = table

    def create_input(self, parent, position, size, placeholder, style, widget_id=None):
        input_field = QLineEdit(parent)
        input_field.setGeometry(position[0], position[1], size[0], size[1])
        input_field.setPlaceholderText(placeholder)
        self.apply_style(input_field, style)

        if widget_id:
            self.widgets[widget_id] = input_field

    def create_dropdown(self, parent, options, position, size, style, widget_id=None):
        dropdown = QComboBox(parent)
        dropdown.setGeometry(position[0], position[1], size[0], size[1])
        dropdown.addItems(options)
        self.apply_style(dropdown, style)

        if widget_id:
            self.widgets[widget_id] = dropdown

    def apply_style(self, widget, style, append=None):
        stylesheet = ""
        for key, value in style.items():
            stylesheet += f"{key}: {value}; "
        if append:
            stylesheet += append

        print("STYLESHEET:", stylesheet)
        print()
        widget.setStyleSheet(stylesheet)

    def handle_actions(self, actions):
        for action in actions:
            output_target = action.get("outputTarget", None)
            target_widget = self.widgets.get(output_target, None)
            action_task = ActionTask(action, self.function_map, target_widget)
            action_task.signals.result.connect(lambda result: self.handle_result(result, target_widget))
            self.threadpool.start(action_task)

    def handle_result(self, result, target_widget):
        if isinstance(target_widget, QTableWidget):
            self.populate_table(result, target_widget)
        elif isinstance(target_widget, QLabel):
            target_widget.setText(result)

    def populate_table(self, result, table):
        """
        Populate the table with data and apply the styles using the 'cellStyle' custom property.
        """
        rows = result.split("\n")
        table.setRowCount(len(rows))

        # Retrieve the cell style from the table's 'cellStyle' property
        cell_style = table.property("cellStyle")
        background_color = cell_style.get("background-color", "#FFFFFF")
        text_color = cell_style.get("color", "#000000")
        font_size = cell_style.get("font-size", 12)
        alignment = cell_style.get("alignment", Qt.AlignCenter)

        for i, row in enumerate(rows):
            columns = row.split(",")
            table.setColumnCount(len(columns))
            for j, column in enumerate(columns):
                cell_item = QTableWidgetItem(column)

                # Apply styles to the cell
                cell_item.setBackground(QtGui.QColor(background_color))
                cell_item.setForeground(QtGui.QColor(text_color))
                cell_item.setFont(QtGui.QFont("Arial", int(font_size)))
                cell_item.setTextAlignment(alignment)

                # Add the cell to the table
                table.setItem(i, j, cell_item)

    def greet_user(self):
        return "Hello from Python!"

    def post_action_message(self):
        return "Post action message: Operation completed successfully!"


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = CustomWidgetApp("widgets_config.json")
    window.show()

    sys.exit(app.exec())
