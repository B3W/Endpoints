import conversationframe as cf
import menubar as mb
import shared
import sidebar as sb
import tkinter as tk
from tkinter import ttk
import queue


class EndpointUI(ttk.Frame):
    '''Top-level container for Endpoint UI'''
    _MSG_POLL_DELAY_MS = 500

    def __init__(self, master, host_id, send_q, recv_q, *args, **kwargs):
        # Initialize root window
        ttk.Frame.__init__(self, master, *args, **kwargs)
        master.title('Endpoint Test UI')

        self.recv_q = recv_q
        self.mpoll_id = None

        # Configure root window
        master.eval('tk::PlaceWindow %s center' % master.winfo_toplevel())
        # master.protocol('WM_DELETE_WINDOW', self.__window_close_callback)

        # Initialize root window grid
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        master.minsize(width=400, height=200)

        # Root frame grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=4)
        self.rowconfigure(0, weight=1)

        # Place root frame
        self.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        # Configure window menu
        self.menu = mb.MenuBar(master, master.destroy)
        master.configure(menu=self.menu)

        # Configure side bar
        self.side_panel = sb.SideBar(self)
        self.side_panel.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        # Configure main area
        self.conversation = cf.ConversationFrame(self, host_id, send_q)
        self.conversation.grid(column=1, row=0,
                               sticky=(tk.N, tk.S, tk.E, tk.W))

        # Begin polling of reception queue
        self.__recv_msg_poll()

    # CALLBACKS
    def __recv_msg_poll(self):
        # Check for a message in the reception queue
        try:
            queue_item = self.recv_q.get_nowait()  # Get and decode msg
            ident, unfmt_ts, msg = shared.decode(queue_item)
            ts = shared.format_timestamp(unfmt_ts)

            self.conversation.add_text_message(ident, ts, msg)  # Send to UI
            self.recv_q.task_done()  # Mark complete

        except queue.Empty:
            pass

        # Register callback to poll queue again. Track ID for cancelling
        self.mpoll_id = self.after(EndpointUI._MSG_POLL_DELAY_MS,
                                   self.__recv_msg_poll)
