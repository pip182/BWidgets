Here's a **README.md** file that provides a comprehensive explanation of the configuration system, including all available options and their possible values.

---

### README.md

```markdown
# Desktop Widgets System

This project provides a customizable desktop widget system using PySide6. Each widget container is defined in a JSON configuration file (`widgets_config.json`), allowing dynamic creation of widgets, layouts, and behaviors.

## How the Configuration Works

The configuration file is a JSON object with the following structure:

### Structure

```json
{
  "user_config": {
    "user": "Alice",
    "theme": "dark"
  },
  "Widget Container1": {
    "title": "System Monitor",
    "geometry": [50, 50, 800, 600],
    "z-order": "always_above",
    "frameless": true,
    "style": {
      "background-color": "#333333",
      "color": "white",
      "border": "2px solid #555"
    },
    "layout": "QGridLayout",
    "widgets": [
      {
        "type": "label",
        "text": "System Monitor",
        "row": 0,
        "column": 0,
        "size": {"width": 400, "height": 50},
        "style": {
          "font-size": "18px",
          "font-weight": "bold",
          "color": "white"
        }
      }
    ]
  }
}
```

---

## Configuration Options

### `user_config`
Defines global settings for the user.
- **`user`** (string): The name of the user.
- **`theme`** (string): UI theme (e.g., `dark`, `light`).

---

### `Widget Container`

Each widget container corresponds to a separate window.

#### Properties

- **`title`** (string): The title of the window (displayed in the title bar unless frameless).
- **`geometry`** (array): The size and position of the window. Format: `[x, y, width, height]`.
  - `x` (int): Horizontal position on the screen.
  - `y` (int): Vertical position on the screen.
  - `width` (int): Width of the window.
  - `height` (int): Height of the window.
- **`z-order`** (string, optional):
  - `"always_above"`: Window stays on top of all others.
  - `"always_below"`: Window stays below all others.
- **`frameless`** (boolean, optional):
  - `true`: Removes the window border.
  - `false` (default): Keeps the standard window frame.
- **`style`** (object, optional): CSS-like styling for the window. Possible keys:
  - `background-color`: Background color of the window.
  - `color`: Default font color for the window.
  - `border`: Border style for the window (e.g., `2px solid #555`).
- **`layout`** (string): Layout type for arranging widgets inside the container.
  - `"QVBoxLayout"`: Vertical arrangement of widgets.
  - `"QHBoxLayout"`: Horizontal arrangement of widgets.
  - `"QGridLayout"`: Grid arrangement of widgets.
- **`widgets`** (array): List of widgets in the container.

---

### `widgets`

Each widget represents a UI component. Available widget types and their properties are listed below.

#### Common Widget Properties

- **`type`** (string): Type of the widget. (See below for supported types.)
- **`size`** (object, optional): The size of the widget.
  - `width` (int): Width of the widget.
  - `height` (int): Height of the widget.
- **`style`** (object, optional): CSS-like styling specific to the widget. Possible keys:
  - `font-size`: Font size for the widget text.
  - `font-weight`: Font weight (e.g., `bold`).
  - `color`: Text color.
  - `background-color`: Background color.

---

### Supported Widget Types

#### 1. `label`

A text label.

**Properties**:
- **`text`** (string): The text displayed by the label.

---

#### 2. `latency_chart`

A line chart displaying network latency to a target host.

**Properties**:
- **`target_host`** (string): The host to ping.
- **`interval`** (int): Update interval in milliseconds.
- **`max_points`** (int): Maximum number of points displayed in the chart.
- **`irregular_factor`** (float): Threshold multiplier for irregular latencies.

---

#### 3. `button`

A clickable button.

**Properties**:
- **`text`** (string): The button label.
- **`action`** (array): List of actions triggered by the button.
  - **`type`** (string): Action type (`notification`, `python`).
  - **`message`** (string, optional): For `notification`, the message to display.

---

#### 4. `timer`

A countdown timer.

**Properties**:
- **`duration`** (int): Timer duration in seconds.
- **`title`** (string, optional): Title for the timer widget.

---

#### 5. `table`

A table displaying static or dynamic data.

**Properties**:
- **`data`** (array): 2D array of table rows and columns.

---

#### 6. `dropdown`

A dropdown menu.

**Properties**:
- **`options`** (array): List of selectable options.
- **`action`** (array, optional): Actions triggered when an option is selected.

---

### Example Configuration

```json
{
  "user_config": {
    "user": "Alice",
    "theme": "dark"
  },
  "Widget Container1": {
    "title": "System Monitor",
    "geometry": [50, 50, 800, 600],
    "z-order": "always_above",
    "frameless": true,
    "style": {
      "background-color": "#333333",
      "color": "white",
      "border": "2px solid #555"
    },
    "layout": "QGridLayout",
    "widgets": [
      {
        "type": "label",
        "text": "System Monitor",
        "row": 0,
        "column": 0,
        "size": {"width": 400, "height": 50},
        "style": {
          "font-size": "18px",
          "font-weight": "bold",
          "color": "white"
        }
      },
      {
        "type": "latency_chart",
        "target_host": "google.com",
        "interval": 1000,
        "max_points": 180,
        "irregular_factor": 3,
        "row": 1,
        "column": 0,
        "size": {"width": 600, "height": 300},
        "style": {
          "background-color": "#222222",
          "font-size": "14px"
        }
      }
    ]
  }
}
```

---

## Features Summary

- **Multiple Windows**: Each container corresponds to a separate window.
- **Dynamic Layouts**: Use vertical, horizontal, or grid layouts for widgets.
- **Z-Order Management**: Set windows to stay "always above" or "always below".
- **Frameless Windows**: Create borderless windows for a cleaner UI.
- **Widget Styling**: Customize widget colors, fonts, sizes, and borders.
