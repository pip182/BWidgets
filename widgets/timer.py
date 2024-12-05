from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QLabel
from widgets.base_widget import BaseWidget


class TimerWidget(BaseWidget):
    def __init__(self, duration, alignment="center", margins=None, style=None, *args, **kwargs):
        self.time_left = duration
        self.timer = QTimer()

        self.label = QLabel(f"Time Left: {self.time_left} seconds")
        self.label.setAlignment(Qt.AlignCenter)

        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

        super().__init__(self.label, alignment=alignment, margins=margins, style=style, *args, **kwargs)

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.label.setText(f"Time Left: {self.time_left} seconds")
        else:
            self.timer.stop()
            self.label.setText("Time's up!")
