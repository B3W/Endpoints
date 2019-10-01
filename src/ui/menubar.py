'''
Module providing Menu implementation for top level window's menu bar.
'''
import tkinter as tk


class MenuBar(tk.Menu):
    '''
    Menu implementation providing menu bar for window
    '''
    def __init__(self, master, exit_callback, *args, **kwargs):
        # Initialize menu bar to place submenus into
        tk.Menu.__init__(self, master, *args, **kwargs)

        self.__create_menu(exit_callback)  # Create submenus

    def __create_menu(self, exit_callback):
        # Create file menu
        self.file_menu = tk.Menu(master=self, tearoff=False)

        # TODO Add file menu items (order matters)
        self.file_menu.add_command(label='Exit', command=exit_callback)

        # Create help menu
        self.help_menu = tk.Menu(master=self, tearoff=False)

        # TODO Add help menu items (order matters)
        self.help_menu.add_command(label='About')

        # Add menus to menu bar (order added == left-to-right order)
        self.add_cascade(label='File', menu=self.file_menu)
        self.add_cascade(label='Help', menu=self.help_menu)
