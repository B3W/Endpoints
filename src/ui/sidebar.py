'''
Module providing the side panel UI elements.
'''
import connectionwidget as cw
import customlistbox as clb
import tkinter as tk
from tkinter import ttk


class SideBar(ttk.Frame):
    '''UI element representing the side panel'''
    def __init__(self, master,
                 add_callback, activate_callback, remove_callback,
                 *args, **kwargs):
        '''
        Initializes the SideBar

        :param master: Master widget that SideBar is child of
        :param add_callback: Adds conversation to ConversationFrame
        :param activate_callback: Activates conversation in ConversationFrame
        :param remove_callback: Deletes conversation from ConversationFrame
        '''
        ttk.Frame.__init__(self, master, *args, **kwargs)  # Init root frame

        self.add_callback = add_callback
        self.activate_callback = activate_callback
        self.remove_callback = remove_callback

        # Root frame grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Create and place listbox
        self.listbox = clb.CustomListbox(self, style='Listbox.TFrame')
        self.listbox.grid(column=0, row=0, sticky=tk.NSEW)

        self.listbox.bind('<<ListboxSelect>>', self.__on_connection_select)

    def report_connection(self, ident, conn_name):
        '''
        Append connection to end of list

        :param ident: ID of connection to append
        :param conn: Friendly name to append
        '''
        # Initialize conversation for ConversationFrame
        self.add_callback(ident, conn_name)

        # Add connection to sidebar
        widget = cw.ConnectionWidget(self.listbox.widget_frame,
                                     ident,
                                     conn_name)

        self.listbox.insert(tk.END, widget)

    def remove_connection(self, ident):
        '''
        Remove connection with ID 'ident' if it exists.

        :param ident: ID of connection to remove
        '''
        # Get the widget associated with the ID
        index = -1
        counter = 0

        for widget in self.listbox.get(0, tk.END):
            if widget.guid == ident:
                index = counter

            counter += 1

        if index == -1:
            # ID not found
            return

        # Remove connection from sidebar
        self.listbox.delete(index)

        # Remove conversation from ConversationFrame
        self.remove_callback(ident)

    # CALLBACKS
    def __on_connection_select(self, event):
        widget = event.widget

        # Determine connection to activate
        try:
            index = int(widget.curselection()[0])

        except IndexError:
            # 'curselection' returned empty list
            return

        connection = widget.get(index)

        # Notify ConversationFrame of activation
        self.activate_callback(connection.ident)
