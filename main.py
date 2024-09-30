import sys
from PyQt6.QtWidgets import QApplication
from gui import DraggableStyledWidget


def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)
    window = DraggableStyledWidget()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
