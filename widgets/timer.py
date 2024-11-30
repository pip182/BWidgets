
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import QTimer
from widgets.base_widget import BaseWidget


class TimerWidget(BaseWidget):
    """Countdown timer widget."""

    def __init__(self, duration, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.duration = duration
        self.label = QLabel(f"Time Remaining: {duration}s", self)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

    def update_timer(self):
        """Update the remaining time and stop when complete."""
        self.duration -= 1
        self.label.setText(f"Time Remaining: {self.duration}s")
        if self.duration <= 0:
            self.timer.stop()
