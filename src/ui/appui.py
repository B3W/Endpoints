import conversationframe as cf
from fonts import Fonts
import menubar as mb
import datapassing_protocol as dproto
import sidebar as sb
import tkinter as tk
from tkinter import ttk
import queue


class EndpointUI(ttk.Frame):
    '''Top-level container for Endpoint UI'''
    _POLL_DELAY_MS = 200   # How often to poll data queue

    def __init__(self, master, host_guid, in_q, *args, **kwargs):
        '''
        :param in_q: Queue for data coming from backend to GUI
        '''
        # Initialize root window
        ttk.Frame.__init__(self, master, *args, **kwargs)
        master.title(f'Endpoints')

        # Configure fonts
        Fonts.init()

        # Configure Styles
        style = ttk.Style()

        # MessageFrame styles
        style.configure('MsgAuthor.TLabel',
                        foreground='dark grey',
                        font=Fonts.get('MessageAuthor'))

        style.configure('MsgAuthorHost.TLabel',
                        foreground='light red',
                        font=Fonts.get('MessageAuthor'))

        style.configure('MsgTimestamp.TLabel',
                        foreground='grey',
                        font=Fonts.get('MessageTimestamp'))

        style.configure('EmptyArea.TLabel',
                        foreground='grey',
                        anchor=tk.CENTER,
                        font=Fonts.get('EmptyArea'))

        self.poll_id = None

        # Configure root window
        master.eval('tk::PlaceWindow %s center' % master.winfo_toplevel())
        # master.protocol('WM_DELETE_WINDOW', self.__window_close_callback)

        # Initialize root window grid
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        master.minsize(width=700, height=400)

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
        self.convo_mgr = cf.ConversationFrame(self, host_guid)
        self.convo_mgr.grid(column=1, row=0,
                            sticky=(tk.N, tk.S, tk.E, tk.W))

        # Configure side bar
        self.side_panel = sb.SideBar(self,
                                     self.convo_mgr.add_conversation,
                                     self.convo_mgr.activate_conversation,
                                     self.convo_mgr.remove_conversation)

        self.side_panel.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        # Begin polling of queues
        self.__poll(in_q)

    # CALLBACKS
    def __poll(self, data_q):
        '''Indefinitely polls queue 'data_q' for new data'''
        try:
            # Retrieve and decode data from queue
            qdata = data_q.get_nowait()

            if qdata.msg_type == dproto.DPMsgType.DPMSG_TYPE_TEXT_MSG:
                # Report message to the ConversationFrame
                self.convo_mgr.report_text_message(qdata.destination_id,
                                                   qdata.timestamp,
                                                   qdata.data)
                data_q.task_done()  # Mark complete

            elif qdata.msg_type == dproto.DPMsgType.DPMSG_TYPE_CONNECTION:
                # Report connection to Sidebar and ConversationFrame
                self.side_panel.report_connection(qdata.endpoint_id,
                                                  qdata.endpoint_name)
                data_q.task_done()  # Mark complete

            elif qdata.msg_type == dproto.DPMsgType.DPMSG_TYPE_DISCONNECT:
                # Report disconnection to Sidebar and ConversationFrame
                self.side_panel.remove_connection(qdata.endpoint_id)
                data_q.task_done()  # Mark complete

        except queue.Empty:
            pass  # No data in queue

        # Register callback to poll queue again. Track ID for cancelling.
        self.poll_id = self.after(EndpointUI._POLL_DELAY_MS,
                                  self.__poll, data_q)
