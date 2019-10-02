'''
'''
import autoscrollbar as asb
import tkinter as tk
from tkinter import ttk


class MessageFrame(ttk.Frame):
    '''
    UI element displaying the actual messages
    '''
    _SENT_COL = 1
    _SENT_STICKY = (tk.E,)  # Side for sent messages to appear in msg frame
    _RECV_COL = 0
    _RECV_STICKY = (tk.W,)  # Side for received messages to appear in msg frame

    def __init__(self, master, host_id, *args, **kwargs):
        '''
        Initializes the MessageFrame

        :param master: The container holding this frame
        :param host_id: Unique id for the host running the application
        '''
        self.host_id = host_id
        self.num_msgs = 0  # Number of messages displayed

        # Initialize frame holding Canvas
        ttk.Frame.__init__(self, master, *args, **kwargs)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=1)

        # Initialize Canvas to hold 'scrollable' frame
        self.canvas = tk.Canvas(self, bg='red')
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

    def add_message(self, msg, sender_id):
        if not msg:
            # Ignore empty messages
            return

        label = ttk.Label(self.msg_frame, text=msg)

        if sender_id == self.host_id:
            # The host sent this message
            label.grid(column=MessageFrame._SENT_COL,
                       row=self.num_msgs,
                       sticky=MessageFrame._SENT_STICKY)

        else:
            # Someone other than the host sent the message
            label.grid(column=MessageFrame._RECV_COL,
                       row=self.num_msgs,
                       sticky=MessageFrame._RECV_STICKY)

        self.num_msgs += 1

    def __on_canvas_configure(self, event):
        new_canvas_width = event.width
        self.canvas.itemconfigure(self.canvas_frame_id, width=new_canvas_width)

    def __update_scrollregion(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL))


class ConversationArea(ttk.Frame):
    '''
    UI element displaying all relevant information of the current conversation
    '''
    _ENTRY_ROW_PAD = 20  # Padding for row containing msg entry/msg send btn
    _ENTRY_X_PAD = (20, 0)  # 'X' pad for msg entry (l-pad, r-pad)
    _SEND_BTN_X_PAD = (0, 20)  # 'X' pad for send btn (l-pad, r-pad)
    _MSG_FRAME_X_PAD = (20, 20)  # 'X' pad around msg frame
    _MSG_FRAME_Y_PAD = (10, 10)  # 'Y' pad around msg frame

    def __init__(self, master, *args, **kwargs):
        # Initialize frame
        ttk.Frame.__init__(self, master, *args, **kwargs)

        # Configure frame's grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=4)
        self.rowconfigure(1, weight=0, pad=ConversationArea._ENTRY_ROW_PAD)

        # MessageFrame for holding the actual messages.
        # NOTE  MessageFrames are only for displaying the messages. All info
        #       relevant to the messages/conversation is tracked elsewhere
        self.msg_display = MessageFrame(self, 'dummy_id')

        # Entry area for entering a new message
        self.msg_entry = ttk.Entry(self)

        # Send button for sending the content in the message entry
        self.msg_send = ttk.Button(self, text='Send')

        # Place widgets
        self.msg_display.grid(column=0, row=0, columnspan=2,
                              padx=ConversationArea._MSG_FRAME_X_PAD,
                              pady=ConversationArea._MSG_FRAME_Y_PAD,
                              sticky=(tk.N, tk.S, tk.E, tk.W))

        self.msg_entry.grid(column=0, row=1,
                            padx=ConversationArea._ENTRY_X_PAD,
                            sticky=(tk.E, tk.W))

        self.msg_send.grid(column=1, row=1,
                           padx=ConversationArea._SEND_BTN_X_PAD,
                           sticky=(tk.W,))

        # Populate dummy messages
        for i in range(30):
            sender_id = 'None'
            if (i % 5) == 0:
                sender_id = 'dummy_id'

            self.msg_display.add_message('item %d' % i, sender_id)
