'''
'''
import tkinter as tk
from tkinter import ttk


class MessageWidget(ttk.Frame):
    '''
    '''
    def __init__(self, master, timestamp, *args, **kwargs):
        ttk.Frame.__init__(self, master, *args, **kwargs)

        # Initialize root grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)

        # Main message area
        self.text = tk.Text(self, relief=tk.FLAT, wrap='word', height=2)
        self.img = None

        # Timestamp
        self.timestamp = ttk.Label(self, text=timestamp,
                                   style='timestamp.TLabel')
        self.timestamp.grid(column=0, row=0, sticky=tk.W)

    def set_text(self, text):
        # Insert and place text
        self.text.insert(1.0, text)
        self.text.config(state=tk.DISABLED)
        self.text.grid(column=0, row=1)

    def set_img(self, img):
        # Create and place img
        self.img = ttk.Label(self, img=img)
        self.img.grid(column=0, row=1)
