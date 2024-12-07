Here’s the updated `README.md` reflecting the change from JSON to YAML configuration:

---

### `README.md`

# Widget Application

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

## Configuration File: `config.yaml`

The configuration file defines the layout, behavior, and appearance of widgets and their containers. It uses the YAML format, replacing the previous JSON configuration.

### Example Configuration

```yaml
user_config:
  user: "Alice"
  theme: "dark"

Widget Container1:
  title: "System Monitor"
  debug: true
  geometry: [50, 50, 800, 400]
  layout: "vertical"
  z-order: "always_above"
  frameless: true
  padding: [10, 10, 10, 10]
  margins: [20, 20, 20, 20]
  widgets:
    - type: "label"
      text: "System Monitor"
      alignment: "center"
      size:
        width: 300
        height: 20
      margins: [5, 5, 5, 5]
      style:
        color: "white"
        font-size: "18px"
        font-weight: "bold"

    - type: "latency_chart"
      target_host: "google.com"
      interval: 1000
      max_points: 180
      irregular_factor: 3
      size:
        width: 600
        height: 300
      margins: [10, 10, 10, 10]
      style:
        background-color: "#ffffff"
        color: "#666"
        font-size: "14px"

    - type: "button"
      text: "Run Diagnostics"
      action:
        - type: "notification"
          message: "Diagnostics started."
      size:
        width: 200
        height: 50
      margins: [5, 5, 5, 5]
      style:
        background-color: "lightblue"
        font-size: "14px"
```

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

## Changes from Previous Versions
- **Configuration Format**:
  - Switched from JSON to YAML for improved readability.
  - Configurations are now stored in `config.yaml`.

- **Centralized Widget Logic**:
  - Widgets inherit alignment, margins, and styling functionality from `BaseWidget`.

---
