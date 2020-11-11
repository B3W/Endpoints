'''
'''
import tkinter as tk
from tkinter import ttk
from fonts import Fonts
from resizabletext import ResizableText
from scrollableframe import WidgetType


class MessageWidget(ttk.Frame):
    '''
    '''
    def __init__(self, master, timestamp_lbl, *args, **kwargs):
        ttk.Frame.__init__(self, master, *args, **kwargs)
        self.author_guid = b''
        self.author_name = ''
        self.is_host = False
        self.visible = False
        self.wtype = WidgetType.WTYPE_LEAF
        self.depth = 0

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
        self.text.wtype = WidgetType.WTYPE_LEAF
        self.text.depth = self.master.depth + 1

        # Author ID
        self.author_lbl = ttk.Label(self)
        self.author_lbl.wtype = WidgetType.WTYPE_LEAF
        self.author_lbl.depth = self.master.depth + 1

        # Timestamp
        self.timestamp_lbl = ttk.Label(self,
                                       text=timestamp_lbl,
                                       style='MsgTimestamp.TLabel')
        self.timestamp_lbl.wtype = WidgetType.WTYPE_LEAF
        self.timestamp_lbl.depth = self.master.depth + 1

    def set_text(self, text):
        # Insert and place text
        self.text.insert(1.0, text)
        self.text.config(state=tk.DISABLED)

    def set_author(self, author_name, author_guid, is_host):
        self.author_guid = author_guid
        self.author_name = author_name
        self.is_host = is_host

        name_len = len(author_name)
        if name_len > 25:
            author_name = author_name[:name_len - 3] + '...'

        if is_host:
            self.author_lbl.configure(text=author_name,
                                      style='MsgAuthorHost.TLabel')
        else:
            self.author_lbl.configure(text=author_name,
                                      style='MsgAuthor.TLabel')

    def place_message(self, sticky):
        # Places message widget on specific side
        if tk.W in sticky:
            self.author_lbl.pack(side=tk.TOP, anchor=tk.W)
            self.timestamp_lbl.pack(side=tk.TOP, anchor=tk.W)
            self.text.pack(side=tk.LEFT, fill=tk.X, expand=True)

        else:
            self.timestamp_lbl.pack(side=tk.TOP, anchor=tk.E)
            self.author_lbl.pack(side=tk.TOP, anchor=tk.E)
            self.text.pack(side=tk.RIGHT, fill=tk.X, expand=True)

    def set_visible(self):
        self.visible = True
        self.bind('<Configure>', self.text.on_configure)

    def set_hidden(self):
        self.visible = False
        self.unbind('<Configure>')
