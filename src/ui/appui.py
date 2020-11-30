import conversationframe as cf
from fonts import Fonts
import menubar as mb
import datapassing_protocol as dproto
import sidebar as sb
import tkinter as tk
from tkinter import ttk
import queue
import logging

_g_logger = logging.getLogger(__name__)


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
        master.configure(background='gray95')

        # Configure fonts
        Fonts.init()

        # Configure Styles
        style = ttk.Style()

        # MessageFrame styles
        style.configure('MsgAuthor.TLabel',
                        foreground='dark gray',
                        font=Fonts.get('MessageAuthor'))

        style.configure('MsgAuthorHost.TLabel',
                        foreground='tomato',
                        font=Fonts.get('MessageAuthor'))

        style.configure('MsgTimestamp.TLabel',
                        foreground='gray',
                        font=Fonts.get('MessageTimestamp'))

        style.configure('EntryArea.TFrame',
                        background='gray95')

        style.configure('EmptyArea.TLabel',
                        foreground='gray',
                        anchor=tk.CENTER,
                        font=Fonts.get('EmptyArea'))

        style.configure('Sidebar.TFrame',
                        background='white')

        style.configure('Listbox.TFrame',
                        background='white')

        style.configure('ConnectionWidget.TFrame',
                        background='white')

        style.configure('Unselected.ConnectionWidget.TFrame',
                        background='white')

        style.configure('Selected.ConnectionWidget.TFrame',
                        background='light sky blue')

        style.configure('ConnectionWidget.TLabel',
                        background='white',
                        anchor=tk.W,
                        padding=(5, 15))

        style.configure('Unselected.ConnectionWidget.TLabel',
                        background='white')

        style.configure('Selected.ConnectionWidget.TLabel',
                        background='light sky blue')

        style.configure('AboutMain.TLabel',
                        font=Fonts.get('AboutMain'))

        self.poll_id = None

        # Configure root window
        master.eval('tk::PlaceWindow %s center' % master.winfo_toplevel())
        # master.protocol('WM_DELETE_WINDOW', self.__window_close_callback)

        # Initialize root window grid
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        master.minsize(width=600, height=300)

        # Root frame grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Place root frame
        self.grid(column=0, row=0, sticky=tk.NSEW)

        # Configure window menu
        self.menu = mb.MenuBar(master, master.destroy)
        master.configure(menu=self.menu)

        # Paned window to hold the conversation area
        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.grid(column=0, row=0, sticky=tk.NSEW)

        # Configure main area
        self.convo_mgr = cf.ConversationFrame(self, host_guid)

        # Configure side bar
        self.side_panel = sb.SideBar(self,
                                     self.convo_mgr.add_conversation,
                                     self.convo_mgr.activate_conversation,
                                     self.convo_mgr.remove_conversation,
                                     style='Sidebar.TFrame')

        # Place sidebar in left pane and conversation area in right pane
        self.paned_window.add(self.side_panel)
        self.paned_window.add(self.convo_mgr)

        # Place window in the center of the screen
        self.master.update_idletasks()
        w = self.master.winfo_width()
        h = self.master.winfo_height()
        wscreen = self.winfo_screenwidth()
        hscreen = self.winfo_screenheight()

        x = (wscreen / 2) - (w / 2)
        y = (hscreen / 2) - (h / 2)

        self.master.geometry(f'{int(w)}x{int(h)}+{int(x)}+{int(y)}')

        # Begin polling of queues
        self.__poll(in_q)

    # CALLBACKS
    def __poll(self, data_q):
        '''Indefinitely polls queue 'data_q' for new data'''
        try:
            # Retrieve and decode data from queue
            qdata = data_q.get_nowait()

            if qdata.msg_type == dproto.DPMsgType.DPMSG_TYPE_TEXT_MSG:
                # Report message to the Sidebar
                self.side_panel.report_message(qdata.destination_id)

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

            else:
                # Invalid queue data
                _g_logger.debug('Invalid message on queue')

        except queue.Empty:
            pass  # No data in queue

        # Register callback to poll queue again. Track ID for cancelling.
        self.poll_id = self.after(EndpointUI._POLL_DELAY_MS,
                                  self.__poll, data_q)
