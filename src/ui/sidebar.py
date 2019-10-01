'''
Module providing the side panel UI elements.
'''
import autoscrollbar as asb
import tkinter as tk
from tkinter import ttk


class SideBar(ttk.Frame):
    '''
    UI object representing the side panel
    '''
    def __init__(self, master, *args, **kwargs):
        '''
        Initializes the SideBar

        :param master: Master widget that SideBar is child of
        '''
        ttk.Frame.__init__(self, master, *args, **kwargs)  # Init root frame
        self.pack(fill=tk.BOTH)  # Space for widgets to occupy

        # Root frame grid
        self.columnconfigure(0, weight=1)  # Listbox col
        self.columnconfigure(1, weight=0)  # Scrollbar col
        self.rowconfigure(0, weight=1)  # Listbox row
        self.rowconfigure(1, weight=0)  # Scrollbar row

        # Create and place scrollbars
        self._vscroll = asb.AutoScrollbar(self, column=1, row=0,
                                          orient=tk.VERTICAL)
        self._hscroll = asb.AutoScrollbar(self, column=0, row=1,
                                          orient=tk.HORIZONTAL)

        # Create and place listbox
        self.listbox = tk.Listbox(self,
                                  selectmode=tk.BROWSE,
                                  activestyle=tk.NONE,
                                  relief=tk.FLAT,
                                  highlightthickness=0,
                                  yscrollcommand=self._vscroll.set,
                                  xscrollcommand=self._hscroll.set)

        self.listbox.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        # Link scrollbars with listbox
        self._vscroll.config(command=self.listbox.yview)
        self._hscroll.config(command=self.listbox.xview)

    def append(self, items):
        '''
        Append 'items' to the end

        :param items: String or iterable of strings to append
        '''
        self.listbox.insert(tk.END, items)

    def insert(self, pos, items):
        '''
        Insert 'items' starting at 'pos'

        :param pos: Index to start insertion at
        :param items: String or iterable of strings to insert
        '''
        self.listbox.insert(pos, items)

    def remove_item(self, item):
        '''
        Remove 'item' if it exists. Only the first occurence of 'item'
        will be removed

        :param item: String to remove
        '''
        cur_items = self.listbox.get(0, tk.END)

        try:
            item_index = cur_items.index(item)
            self.remove_range(item_index)

        except ValueError:
            # 'item' not found in listbox
            pass

    def remove_range(self, start, end=None):
        '''
        Remove items from 'start' to 'end' (inclusive). Omit 'end' to only
        remove the item at index 'start'.

        :param start: Index to begin removal
        :param end: Index to end removal
        '''
        if end:
            self.listbox.delete(start, end)
        else:
            self.listbox.delete(start)
