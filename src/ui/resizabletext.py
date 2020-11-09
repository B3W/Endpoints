'''Module providing resizable text widget'''
import tkinter as tk
import math


class ResizableText(tk.Text):
    def __init__(self, master, fixed_font, *args, **kwargs):
        tk.Text.__init__(self, master, font=fixed_font, *args, **kwargs)
        self.font = fixed_font
        self.line_count = 0
        self._resizing = False

        # Pixel width to font width conversion number
        self._pixel_unit = self.font.measure('0')

        self.bind('<<Modified>>', self.resize)

    def resize(self, event=None):
        widget_width = 0
        resized_line_count = 0
        max_width = self.cget('width')
        lines = self.get('1.0', 'end-1c').splitlines()

        for line in lines:
            line_width = len(line)

            if line_width > max_width:
                widget_width = max_width

                # Calculate number of times line will wrap
                resized_line_count += line_width / max_width

            else:
                widget_width = max(widget_width, line_width)
                resized_line_count += 1

        resized_line_count = math.ceil(resized_line_count)

        # Only configure height if it has changed
        if self.line_count != resized_line_count:
            self.line_count = resized_line_count
            self.configure(height=self.line_count)

        self._resizing = False

    def on_configure(self, event):
        # NOTE 'event.width' is the pixel width of the text
        if event.width <= 1:  # Ignore calls with no width
            return

        # Only resize every ~200ms
        if not self._resizing:
            self._resizing = True

            # Bit of a hack. Text widgets determine their width based on the
            # pixel size of a '0'. Convert the given pixel width to font width
            converted_width = int(event.width / self._pixel_unit)
            self.configure(width=converted_width)

            self.after(200, self.resize)
