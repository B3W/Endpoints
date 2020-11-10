'''
'''
import tkinter as tk
from tkinter import ttk
from fonts import Fonts
from resizabletext import ResizableText


class MessageWidget(ttk.Frame):
    '''
    '''
    def __init__(self, master, timestamp_lbl, *args, **kwargs):
        ttk.Frame.__init__(self, master, *args, **kwargs)
        self.author_guid = b''
        self.visible = False

        # Main message area
        # NOTE  Default height to 1 so that it does not attempt to fill up
        #       available space causing screen flicker and grid calculation lag
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

    def set_visible(self):
        self.visible = True
        self.bind('<Configure>', self.text.on_configure)

    def set_hidden(self):
        self.visible = False
        self.unbind('<Configure>')
