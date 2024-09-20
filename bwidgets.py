import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton







class DraggableWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.oldPos = self.pos()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = event.globalPos() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()





# Step 1: Initialize the application
app = QApplication(sys.argv)

# Step 2: Create the main window (widget)
window = DraggableWidget()

# Set the window title and size
window.setWindowTitle('Desktop Widget')
window.setGeometry(100, 100, 250, 150)

# Step 3: Customize the window flags to make it stay on top and frameless
window.setWindowFlags(Qt.FramelessWindowHint)

# Step 4: Create the layout and add widgets (label and close button)
layout = QVBoxLayout()

label = QLabel('Hello, this is a PyQt5 Widget!', window)
layout.addWidget(label)

# Add a close button
close_button = QPushButton('Close', window)
close_button.clicked.connect(window.close)  # Close the window when clicked
layout.addWidget(close_button)

# Set the layout for the window
window.setLayout(layout)

# Step 5: Show the window
window.show()

# Step 6: Execute the application loop
sys.exit(app.exec_())
