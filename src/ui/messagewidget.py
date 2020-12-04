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
        self.wtype = WidgetType.WTYPE_ROOT_CONTAINER
        self.depth = 0

        # Initialize root grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)

        # Main message area
        # NOTE  Default height to 1 so that it does not attempt to fill up
        #       available space causing screen flicker and grid calculation lag
        self.text = ResizableText(self,
                                  font=Fonts.get('MessageText'),
                                  relief=tk.FLAT,
                                  wrap=tk.WORD,
                                  highlightbackground="light grey",
                                  highlightthickness=2,
                                  height=1)
        self.text.wtype = WidgetType.WTYPE_LEAF
        self.text.depth = self.text.master.depth + 1

        # Frame containing author, timestamp, etc...
        self.metadata_frame = ttk.Frame(self)
        self.metadata_frame.wtype = WidgetType.WTYPE_LEAF
        self.metadata_frame.depth = self.metadata_frame.master.depth + 1
        self.metadata_frame.grid(column=0, row=0, sticky=tk.EW)

        # Author ID
        self.author_lbl = ttk.Label(self.metadata_frame)
        self.author_lbl.wtype = WidgetType.WTYPE_LEAF
        self.author_lbl.depth = self.author_lbl.master.depth + 1

        # Timestamp
        self.timestamp_lbl = ttk.Label(self.metadata_frame,
                                       text=timestamp_lbl,
                                       style='MsgTimestamp.TLabel')
        self.timestamp_lbl.wtype = WidgetType.WTYPE_LEAF
        self.timestamp_lbl.depth = self.timestamp_lbl.master.depth + 1

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
            self.author_lbl.pack(side=tk.LEFT)
            self.timestamp_lbl.pack(side=tk.LEFT)

        else:
            self.timestamp_lbl.pack(side=tk.RIGHT)
            self.author_lbl.pack(side=tk.RIGHT)

        self.text.grid(column=0, row=1, sticky=sticky)

    def set_visible(self):
        self.visible = True
        self.bind('<Configure>', self.text.on_configure)

        # Resize the widget when it is set visible as it does not
        # configuring itself when it is hidden
        self.event_generate('<Configure>')

    def set_hidden(self):
        self.visible = False
        self.unbind('<Configure>')
