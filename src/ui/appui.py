import conversationframe as cf
import menubar as mb
from shared import timeutils as tu
from shared import queueprotocol as qp
import sidebar as sb
import tkinter as tk
from tkinter import ttk
import queue


class EndpointUI(ttk.Frame):
    '''Top-level container for Endpoint UI'''
    # NOTE  Race condition where if message is sent to connection before the
    #       connection queue has been polled message will be dropped
    _CONN_POLL_DELAY_MS = 500   # How often to poll connection queue
    _MSG_POLL_DELAY_MS = 250    # How often to poll received message queue

    def __init__(self,
                 master, host_id, conn_q, send_q, recv_q,
                 *args, **kwargs):
        # Initialize root window
        ttk.Frame.__init__(self, master, *args, **kwargs)
        master.title('Endpoint Test UI')

        self.conn_q = conn_q
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

        # Configure main area
        self.convo_mgr = cf.ConversationFrame(self, host_id, send_q)
        self.convo_mgr.grid(column=1, row=0,
                            sticky=(tk.N, tk.S, tk.E, tk.W))

        # Configure side bar
        self.side_panel = sb.SideBar(self,
                                     self.convo_mgr.add_conversation,
                                     self.convo_mgr.activate_conversation,
                                     self.convo_mgr.remove_conversation)

        self.side_panel.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        # Begin polling of queues
        self.__conn_poll(conn_q)
        self.__recv_msg_poll(recv_q)

    # CALLBACKS
    def __conn_poll(self, conn_q):
        '''
        Indefinitely polls given queue for new connections
        '''
        try:
            # Retrieve and decode connection from queue
            queue_item = conn_q.get_nowait()
            ident, name = qp.conn_decode(queue_item)

            # Report connection to Sidebar and ConversationFrame
            self.side_panel.report_connection(ident, name)
            conn_q.task_done()  # Mark complete

        except queue.Empty:
            # No connection in queue
            pass

        # Register callback to poll queue again. Track ID for cancelling.
        self.cpoll_id = self.after(EndpointUI._CONN_POLL_DELAY_MS,
                                   self.__conn_poll, conn_q)

    def __recv_msg_poll(self, recv_q):
        '''
        Indefinitely polls given queue for new received messages
        '''
        try:
            # Retrieve and decode message from queue
            queue_item = recv_q.get_nowait()
            ident, unfmt_ts, msg = qp.text_decode(queue_item)
            ts = tu.format_timestamp(unfmt_ts)

            # Report message to the ConversationFrame
            self.convo_mgr.report_text_message(ident, ts, msg)
            recv_q.task_done()  # Mark complete

        except queue.Empty:
            # No message in queue
            pass

        # Register callback to poll queue again. Track ID for cancelling.
        self.mpoll_id = self.after(EndpointUI._MSG_POLL_DELAY_MS,
                                   self.__recv_msg_poll, recv_q)
