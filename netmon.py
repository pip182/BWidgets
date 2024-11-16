import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from ping3 import ping
from collections import deque
from tkinter import Tk


# Constants
TARGET_HOST = "192.168.1.106"
MAX_X = 180  # Number of data points to display (e.g., last 360 updates)
INTERVAL = 300  # Update interval in milliseconds (300 ms)
IRREGULAR_LATENCY_FACTOR = 3  # Threshold multiplier for irregular latency


# Hide the Matplotlib toolbar
matplotlib.rcParams['toolbar'] = 'none'


# Data storage
latency_data = deque([0] * MAX_X, maxlen=MAX_X)
lost_packets = 0
total_packets = 0
irregular_latency_count = 0  # Counter for irregular latencies


# Initialize figure and axis with smaller graph size and extra top padding
fig, ax = plt.subplots(figsize=(5, 2))  # Smaller graph
fig.subplots_adjust(top=0.4)  # More padding above the graph
fig.patch.set_facecolor('#2E2E2E')  # Dark background for the figure
ax.set_facecolor('#2E2E2E')  # Dark background for the plot area


# Hide the window frame using tkinter
manager = plt.get_current_fig_manager()
if hasattr(manager, 'window'):
    root = manager.window
    if isinstance(root, Tk):
        root.attributes('-fullscreen', False)  # Not fullscreen
        root.overrideredirect(True)  # Remove window frame


# Configure the line and text colors for a dark theme
latency_line, = ax.plot([], [], label="Latency (ms)", color="cyan")
ax.spines['bottom'].set_color('white')
ax.spines['top'].set_color('white')
ax.spines['right'].set_color('white')
ax.spines['left'].set_color('white')
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')
ax.yaxis.label.set_color('white')
ax.xaxis.label.set_color('white')
ax.title.set_color('white')


# Set up the plot limits and labels
ax.set_xlim(0, MAX_X - 1)
ax.set_ylim(0, 200)  # Adjusted for more vertical space
ax.set_title(f"Latency Monitoring to {TARGET_HOST}")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Latency (ms)")


# Function to create text with a semi-transparent box
def draw_text_with_box(ax, x, y, text, fontsize=10, color="white", box_color="black", alpha=0.5):
    return ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        transform=ax.transAxes,
        fontsize=fontsize,
        color=color,
        bbox=dict(facecolor=box_color, edgecolor="none", alpha=alpha, boxstyle="round,pad=0.3"),
    )


# Function to calculate average latency
def calculate_average_latency(latency_list):
    valid_latencies = [x for x in latency_list if x > 0]
    return sum(valid_latencies) / len(valid_latencies) if valid_latencies else 0


# Update function for animation
def update(frame):
    global total_packets, lost_packets, irregular_latency_count

    # Ping the target host and collect latency data
    latency = ping(TARGET_HOST, timeout=1)
    total_packets += 1

    if latency is None:
        lost_packets += 1
        latency_data.append(0)  # Show 0 latency for lost packets
    else:
        latency_ms = latency * 1000  # Convert to ms
        latency_data.append(latency_ms)

        # Calculate average latency
        avg_latency = calculate_average_latency(latency_data)

        # Check if latency is irregular (greater than 3x the average)
        if avg_latency > 0 and latency_ms > IRREGULAR_LATENCY_FACTOR * avg_latency:
            irregular_latency_count += 1

    # Calculate the current average latency
    avg_latency = calculate_average_latency(latency_data)

    # Update line data
    latency_line.set_data(range(len(latency_data)), latency_data)
    ax.set_ylim(0, max(latency_data) * 1.2 if latency_data else 1)

    # Clear existing texts to avoid overlapping
    for text in ax.texts:
        text.remove()

    # Update top labels with semi-transparent boxes
    draw_text_with_box(ax, 0.5, 0.75, f"Total Packets Sent: {total_packets}")
    draw_text_with_box(ax, 0.5, 0.6, f"Total Packets Lost: {lost_packets}")
    draw_text_with_box(ax, 0.5, 0.40, f"Average Latency: {avg_latency:.2f} ms")
    draw_text_with_box(ax, 0.5, 0.25, f"Irregular Latencies: {irregular_latency_count}")

    return latency_line,


# Run the animation
ani = animation.FuncAnimation(fig, update, interval=INTERVAL)
plt.tight_layout()
plt.show()
