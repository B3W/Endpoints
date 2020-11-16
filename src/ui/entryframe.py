import autoscrollbar as asb
from fonts import Fonts
import multilineentry as me
import tkinter as tk
from tkinter import ttk


class EntryFrame(ttk.Frame):
    '''UI element containing widgets for message compilation.'''
    def __init__(self, master, max_lines, *args, **kwargs):
        '''Override of ttk.Frame's initialization function'''
        # Initialize root frame
        ttk.Frame.__init__(self, master, *args, **kwargs)

        self.columnconfigure(0, weight=1)  # Entry widget
        self.columnconfigure(1, weight=0)  # AutoScrollbar
        self.rowconfigure(0, weight=1)

        self.MAX_LINES = max_lines  # Max number of lines entry will resize to

        # Initialize multiline entry widget
        self.entry = me.MultilineEntry(self,
                                       self.MAX_LINES,
                                       font=Fonts.get('EntryText'),
                                       relief=tk.FLAT,
                                       wrap='word',
                                       highlightbackground="light grey",
                                       highlightthickness=2,
                                       height=1)
        self.entry.grid(column=0, row=0, sticky=tk.EW)

        # Initialize scrollbar
        self.vsb = asb.AutoScrollbar(self, 1, 0, orient=tk.VERTICAL)
        self.entry.configure(yscrollcommand=self.vsb.set)

        self.bind('<Configure>', self.entry.on_configure)
        self.entry.bind('<Return>', self.__on_enter)
        self.entry.bind('<Shift-Return>', self.__on_newline)

    def get(self):
        '''Returns contents of the entry'''
        return self.entry.get(1.0, 'end-1c')

    def clear(self):
        '''Clears contents of the entry'''
        self.entry.delete(1.0, tk.END)

    def focus(self):
        '''Sets application focus to the entry area'''
        self.entry.focus_set()

    def __on_enter(self, event):
        '''Handler for <Return> event'''
        # Generate <<Send>> event when enter key pressed
        self.event_generate('<<Send>>')

        # Stop propagation of event to prevent newline
        return 'break'

    def __on_newline(self, event):
        '''Handler for <Shift-Return> event'''
        # Ignore the event to allow for newlines
        pass
