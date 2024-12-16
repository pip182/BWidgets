from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from widgets.base_widget import BaseWidget
import asyncio


class Label(BaseWidget):
    def __init__(
        self,
        text="",
        alignment="center",
        data_provider=None,
        results_handler=None,
        style=None,
        *args,
        **kwargs,
    ):
        """
        Create a Label widget.

        Args:
            text: Initial text to display.
            alignment: Alignment of the text.
            data_provider: Function or command to fetch dynamic text (optional).
            results_handler: Function to process fetched text (optional).
            style: CSS-like styles for the label (as a dictionary).
        """
        self.label = QLabel(text)
        self.data_provider = data_provider
        self.results_handler = results_handler
        self.style = style or {}

        # Apply alignment
        self.apply_alignment(alignment)

        # Apply styles
        self.apply_styles()

        # Initialize BaseWidget
        super().__init__(self.label, *args, **kwargs)

        # Fetch initial data if data_provider is defined
        if data_provider:
            asyncio.ensure_future(self.refresh_text())

    def apply_alignment(self, alignment):
        """Set the text alignment."""
        alignment_map = {
            "center": Qt.AlignCenter,
            "left": Qt.AlignLeft,
            "right": Qt.AlignRight,
            "top": Qt.AlignTop,
            "bottom": Qt.AlignBottom,
        }
        self.label.setAlignment(alignment_map.get(alignment, Qt.AlignCenter))

    def apply_styles(self):
        """Apply custom styles to the label."""
        stylesheet = ""
        for key, value in self.style.items():
            stylesheet += f"{key}: {value};"
        self.label.setStyleSheet(stylesheet)

    async def refresh_text(self):
        """Fetch dynamic text using the data_provider and update the label."""
        text = await self.fetch_data()
        if text is not None:
            # Process the fetched data with the results_handler, if defined
            if self.results_handler:
                text = self.handle_results(text)
            self.label.setText(text)
