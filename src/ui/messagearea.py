'''
'''
import autoscrollbar as asb
import tkinter as tk
from tkinter import ttk


class MessageFrame(ttk.Frame):
    '''
    UI element displaying the messages
    '''
    _SENT_COL = 1
    _SENT_X_PAD = (0, 20)  # 'X' pad for sent msg (l-pad, r-pad)
    _SENT_STICKY = (tk.E,)  # Side for sent messages to appear in msg frame
    _RECV_COL = 0
    _RECV_X_PAD = (0, 20)  # 'X' pad for recv msg (l-pad, r-pad)
    _RECV_STICKY = (tk.W,)  # Side for received messages to appear in msg frame

    def __init__(self, master, *args, **kwargs):
        '''
        Initializes the MessageFrame

        :param master: The container holding this frame
        '''
        self.num_msgs = 0  # Number of messages displayed

        # Initialize frame holding Canvas
        ttk.Frame.__init__(self, master, *args, **kwargs)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=1)

        # Initialize Canvas to hold 'scrollable' frame
        self.canvas = tk.Canvas(self)
        self.canvas.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        # Initialize vertical AutoScrollbar and link to the Canvas
        self.vsb = asb.AutoScrollbar(self,
                                     column=1, row=0,
                                     orient=tk.VERTICAL,
                                     command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=self.vsb.set)

        # Initialize 'scrollable' frame for actual message content
        self.msg_frame = ttk.Frame(self.canvas)
        self.msg_frame.columnconfigure(0, weight=1)
        self.msg_frame.columnconfigure(1, weight=1)

        canvas_win_location = (0, 0)
        self.canvas_frame_id = self.canvas.create_window(canvas_win_location,
                                                         window=self.msg_frame,
                                                         anchor='nw')

        # Bind callbacks for when the Canvas is resized
        self.msg_frame.bind('<Configure>', self.__update_scrollregion)
        self.canvas.bind('<Configure>', self.__on_canvas_configure)

    def add_message(self, msg, is_host):
        if not msg:
            # Ignore empty messages
            return

        label = ttk.Label(self.msg_frame, text=msg)

        if is_host:
            # The host sent this message
            label.grid(column=MessageFrame._SENT_COL,
                       row=self.num_msgs,
                       sticky=MessageFrame._SENT_STICKY,
                       padx=MessageFrame._SENT_X_PAD)

        else:
            # Someone other than the host sent the message
            label.grid(column=MessageFrame._RECV_COL,
                       row=self.num_msgs,
                       sticky=MessageFrame._RECV_STICKY,
                       padx=MessageFrame._RECV_X_PAD)

        self.num_msgs += 1

    def __on_canvas_configure(self, event):
        new_canvas_width = event.width
        self.canvas.itemconfigure(self.canvas_frame_id, width=new_canvas_width)

    def __update_scrollregion(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL))
        self.canvas.yview_moveto(1.0)  # 'Autoscroll' to bottom of canvas
