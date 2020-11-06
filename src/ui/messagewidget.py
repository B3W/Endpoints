'''
'''
import tkinter as tk
from tkinter import ttk
from fonts import Fonts
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


class MessageWidget(ttk.Frame):
    '''
    '''
    def __init__(self, master, timestamp_lbl, *args, **kwargs):
        ttk.Frame.__init__(self, master, *args, **kwargs)
        self.author_guid = b''

        # Main message area
        # NOTE  Default height to 1 so that it does not attempt to fill up
        #       available space cause screen flicker and grid calculation lag
        self.text = ResizableText(self,
                                  Fonts.get('MessageText'),
                                  relief=tk.FLAT,
                                  wrap='word',
                                  highlightbackground="light grey",
                                  highlightthickness=2,
                                  height=1)

        # Author ID
        self.author_lbl = ttk.Label(self,
                                    text='',
                                    style='MsgAuthor.TLabel')

        # Timestamp
        self.timestamp_lbl = ttk.Label(self,
                                       text=timestamp_lbl,
                                       style='MsgTimestamp.TLabel')

        self.bind('<Configure>', self.text.on_configure)

    def set_text(self, text):
        # Insert and place text
        self.text.insert(1.0, text)
        self.text.config(state=tk.DISABLED)

    def set_author(self, author_name, author_guid):
        self.author_guid = author_guid

        name_len = len(author_name)
        if name_len > 25:
            author_name = author_name[:name_len - 3] + '...'

        self.author_lbl.configure(text=author_name)

    def place_message(self, sticky):
        # Places message widget on specific side
        if tk.W in sticky:
            self.author_lbl.pack(side=tk.TOP, anchor=tk.NW)
            self.timestamp_lbl.pack(side=tk.TOP, anchor=tk.NW)
            self.text.pack(side=tk.LEFT, fill=tk.X, expand=True)

        else:
            self.timestamp_lbl.pack(side=tk.TOP, anchor=tk.NE)
            self.author_lbl.pack(side=tk.TOP, anchor=tk.NE)
            self.text.pack(side=tk.RIGHT, fill=tk.X, expand=True)
