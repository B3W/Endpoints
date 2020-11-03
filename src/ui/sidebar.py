'''
Module providing the side panel UI elements.
'''
import autoscrollbar as asb
import tkinter as tk
from tkinter import ttk


class Connection(object):
    '''Class defining all data related to a connection'''
    def __init__(self, guid, name):
        self.ident = guid
        self.name = name


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

        # List of active connections
        self.connections = []

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

        self.listbox.bind('<<ListboxSelect>>', self.__on_connection_select)

    def report_connection(self, ident, conn_name):
        '''
        Append connection to end of list

        :param ident: ID of connection to append
        :param conn: Friendly name to append
        '''
        # Initialize conversation for ConversationFrame
        self.add_callback(ident)

        # Add connection to sidebar
        self.connections.append(Connection(ident, conn_name))
        self.listbox.insert(tk.END, conn_name)

    def remove_connection(self, ident):
        '''
        Remove connection with ID 'ident' if it exists.

        :param ident: ID of connection to remove
        '''
        # Get the name associated with the ID
        index = self._find_connection_by_id(ident)

        if index == -1:
            # ID not found
            return

        try:
            connection = self.connections[index]
            item_index = self.listbox.get(0, tk.END).index(connection.name)

            # Remove connection from sidebar
            self.connections.remove(connection)
            self.listbox.delete(item_index)

            # Remove conversation from ConversationFrame
            self.remove_callback(ident)

        except ValueError:
            # Connection not found
            pass

    def _find_connection_by_id(self, ident):
        index = -1

        for i in range(len(self.connections)):
            if self.connections[i].ident == ident:
                index = i
                break

        return index

    def _find_connection_by_name(self, name):
        index = -1

        for i in range(len(self.connections)):
            if self.connections[i].name == name:
                index = i
                break

        return index

    # CALLBACKS
    def __on_connection_select(self, event):
        widget = event.widget

        try:
            # Determine connection to activate
            index = int(widget.curselection()[0])

        except IndexError:
            # 'curselection' returned empty list
            return

        conn_name = widget.get(index)

        # Notify ConversationFrame of activation
        index = self._find_connection_by_name(conn_name)

        if index >= 0:
            self.activate_callback(self.connections[index].ident)
