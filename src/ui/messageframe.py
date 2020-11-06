'''
'''
import autoscrollbar as asb
import config as c
import math
import messagewidget as mw
import timeutils
import tkinter as tk
from tkinter import ttk
import logging


_g_logger = logging.getLogger(__name__)


class MessageFrame(ttk.Frame):
    '''UI element displaying the messages of conversation'''
    _SENT_X_PAD = (10, 10)  # 'X' pad for sent msg (l-pad, r-pad)
    _SENT_STICKY = tk.EW  # Side for sent messages to appear in msg frame
    _RECV_X_PAD = (10, 10)  # 'X' pad for recv msg (l-pad, r-pad)
    _RECV_STICKY = tk.EW  # Side for received messages to appear in msg frame
    _MSG_Y_PAD = (20, 0)  # 'Y' pad for all msg (t-pad, b-pad)

    _MOUSEWHEEL_EVENT = '<MouseWheel>'  # Event to bind for mouse wheel scrolls
    host_id = b''  # Universal host ID of the running Endpoint

    def __init__(self, master, name, *args, **kwargs):
        '''
        Initializes the MessageFrame

        :param master: The container holding this frame
        :param name: Friendly name of Endpoint communicating with
        '''
        self.correspondent_name = name
        self.num_msgs = 0  # Number of messages displayed
        self.msgs = []  # List of all messages in the frame

        # Initialize frame holding Canvas
        ttk.Frame.__init__(self, master, *args, **kwargs)

        self.columnconfigure(0, weight=1)  # Canvas/Scrollable Frame
        self.columnconfigure(1, weight=0)  # AutoScrollbar
        self.rowconfigure(0, weight=1)

        # Initialize Canvas to hold 'scrollable' frame
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.grid(column=0, row=0, sticky=tk.NSEW)

        # Initialize vertical AutoScrollbar and link to the Canvas
        self.vsb = asb.AutoScrollbar(self,
                                     column=1, row=0,
                                     orient=tk.VERTICAL,
                                     command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=self.vsb.set)

        # Initialize 'scrollable' frame for actual message content
        self.msg_frame = ttk.Frame(self.canvas)
        self.msg_frame.columnconfigure(0, weight=1)

        canvas_win_location = (0, 0)
        self.canvas_frame_id = self.canvas.create_window(canvas_win_location,
                                                         window=self.msg_frame,
                                                         anchor='nw')

        # Bind callbacks for when the Message Frame/Canvas is resized
        self.msg_frame.bind('<Configure>', self.__update_scrollregion)
        self.canvas.bind('<Configure>', self.__on_canvas_configure)

        # Bind callbacks for the mouse wheel
        self.msg_frame.bind('<Enter>', self.__bind_mousewheel)
        self.msg_frame.bind('<Leave>', self.__unbind_mousewheel)

    def add_text_message(self, ident, timestamp, text):
        '''
        Function for displaying text message

        :param ident: GUID of the message sender
        :param timestamp: ISO formatted timestamp
        :param text: Message data
        '''
        if not text:
            # Ignore empty messages
            return

        # Create and configure message
        fmt_ts = timeutils.format_timestamp(timestamp)
        text_msg = mw.MessageWidget(self.msg_frame, fmt_ts)
        text_msg.set_text(text)

        if ident == c.Config.get(c.ConfigEnum.ENDPOINT_GUID):
            # The host sent this message
            text_msg.set_author('Me', ident)
            text_msg.place_message(MessageFrame._SENT_STICKY)

            text_msg.grid(column=0, row=self.num_msgs,
                          sticky=MessageFrame._SENT_STICKY,
                          padx=MessageFrame._SENT_X_PAD,
                          pady=MessageFrame._MSG_Y_PAD)

        else:
            # Someone other than the host sent the message
            text_msg.set_author(self.correspondent_name, ident)
            text_msg.place_message(MessageFrame._RECV_STICKY)

            text_msg.grid(column=0, row=self.num_msgs,
                          sticky=MessageFrame._RECV_STICKY,
                          padx=MessageFrame._RECV_X_PAD,
                          pady=MessageFrame._MSG_Y_PAD)

        self.msgs.insert(0, text_msg)
        self.num_msgs += 1
        self.__scroll_last_message()

    def __scroll_last_message(self):
        self.canvas.update_idletasks()  # Let canvas finish layout calculations
        self.canvas.yview_moveto(1.0)   # Scroll to bottom of canvas

    # CALLBACKS
    def __on_canvas_configure(self, event):
        canvas_width = event.width
        self.canvas.itemconfigure(self.canvas_frame_id, width=canvas_width)

    def __update_scrollregion(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL))

    def __bind_mousewheel(self, event):
        # Bind the root scrollable widget to the scrolling callback
        self.canvas.bind_all(MessageFrame._MOUSEWHEEL_EVENT,
                             self.__on_mousewheel)

    def __unbind_mousewheel(self, event):
        # Unbind the root scrollable widget from the scrolling callback
        self.canvas.unbind_all(MessageFrame._MOUSEWHEEL_EVENT)

    def __on_mousewheel(self, event):
        # Do not allow scrolling if scrollbars are hidden
        if self.vsb.hidden:
            return

        # Get sign of delta then reverse to get scroll direction
        scroll_dir = -1 * int(math.copysign(1, event.delta))
        self.canvas.yview_scroll(scroll_dir, 'units')
