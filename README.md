### Widget Application

This is a customizable desktop widget application. It allows users to create interactive widgets such as labels, buttons, latency charts, and more, based on a configuration file written in YAML.

---

## Getting Started

1. **Install Dependencies**:
   Ensure you have Python and the required libraries installed:
   ```bash
   pip install PySide6 ping3 pyyaml
   ```

2. **Run the Application**:
   Execute the main script to start the application:
   ```bash
   python main.py
   ```

3. **Edit Configuration**:
   Customize the application using the `config.yaml` file.

---

## Configuration Fields

### General Fields

- **`user_config`**:
  - Defines global settings like user preferences and themes.

### Widget Containers

Each container is a window that contains widgets.

- **`title`** (string): Title of the container window.
- **`geometry`** (list): Defines `[x, y, width, height]` of the window.
- **`layout`** (string): Specifies the layout type (`vertical`, `horizontal`, `grid`).
- **`z-order`** (string): Set window stacking order (`always_above` or `always_below`).
- **`frameless`** (boolean): Whether the container window is frameless.
- **`debug`** (boolean): If `true`, adds green borders around widgets.
- **`padding`** (list): Inner padding for the container layout `[left, top, right, bottom]`.
- **`margins`** (list): Outer margins for the container layout `[left, top, right, bottom]`.

---

### Widgets

#### Common Fields

All widgets support the following fields:

- **`type`** (string): Type of widget (`label`, `button`, `latency_chart`, etc.).
- **`alignment`** (string): Widget alignment (`center`, `left`, `right`, `top`, `bottom`).
- **`size`** (dict): Defines widget size: `{"width": <width>, "height": <height>}`.
- **`margins`** (list): Space around the widget `[left, top, right, bottom]`.
- **`style`** (dict): CSS-like styles for the widget.

---

#### Specific Widgets

1. **Label**
   Displays text on the window.
   ```yaml
   - type: "label"
     text: "System Monitor"
     alignment: "center"
     style:
       font-size: "18px"
       font-weight: "bold"
   ```

2. **Button**
   A clickable button with actions.
   ```yaml
   - type: "button"
     text: "Run Diagnostics"
     action:
       - type: "notification"
         message: "Diagnostics started."
   ```

3. **Dropdown**
   A dropdown menu for selecting options.
   ```yaml
   - type: "dropdown"
     options: ["Option 1", "Option 2"]
     action:
       - type: "notification"
         message: "Option selected."
   ```

4. **Input**
   A text input field.
   ```yaml
   - type: "input"
     placeholder: "Enter your name"
   ```

5. **Latency Chart**
   Displays a real-time latency chart.
   ```yaml
   - type: "latency_chart"
     target_host: "google.com"
     interval: 1000
     max_points: 180
   ```

6. **Table**
   Displays a table of data.
   ```yaml
   - type: "table"
     data:
       - ["Metric", "Value"]
       - ["CPU Usage", "Loading..."]
   ```

7. **Timer**
   Displays a countdown timer.
   ```yaml
   - type: "timer"
     duration: 60
   ```

---

## Data Provider

The `data_provider` field in `config.yaml` allows widgets to dynamically fetch data from various sources. It supports the following types:

1. **Python Functions or Methods**:
   - Specify the full module path to a Python function or method.
   - Example:
     ```yaml
     data_provider: "local_actions.get_user_data"
     ```

2. **Python Classes**:
   - Specify the full module path to a Python class. The class will be instantiated, and if it defines a `__call__` method, that method will be executed.
   - Example:
     ```yaml
     data_provider: "custom_module.CustomClass"
     ```

3. **Shell Commands**:
   - Use a leading `!` to indicate a shell command. The command will be executed, and its output will be used as the data.
   - Example:
     ```yaml
     data_provider: "!ls -la"
     ```

4. **Callable Objects**:
   - You can pass a callable object directly in the Python code instead of using YAML.

---

## Results Handler

The `results-handler` field specifies how the data fetched by `data_provider` is processed and displayed in the widget.

### Example

For a table widget:
```yaml
data_provider: "local_actions.get_user_data"
results-handler:
  type: "table"
  display_fields: ["Name", "Age", "Department"]
```

For a latency chart:
```yaml
data_provider: "tasks.check_ping"
results-handler:
  action: "ping"
  field: "latency"
```

---

## Changes from Previous Versions

- **Data Provider Enhancements**:
  - Supports Python classes, methods, shell commands, and callable objects.
- **Results Handling**:
  - Flexible configuration to process and display dynamic data.

---
