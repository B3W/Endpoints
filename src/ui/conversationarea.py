'''
'''
import messagearea as ma
import tkinter as tk
from tkinter import ttk


class ConversationArea(ttk.Frame):
    '''
    UI element displaying all relevant information of the current conversation
    '''
    _ENTRY_ROW_PAD = 20  # Padding for row containing msg entry/msg send btn
    _ENTRY_X_PAD = (20, 0)  # 'X' pad for msg entry (l-pad, r-pad)
    _SEND_BTN_X_PAD = (0, 20)  # 'X' pad for send btn (l-pad, r-pad)
    _MSG_FRAME_X_PAD = (20, 20)  # 'X' pad around msg frame
    _MSG_FRAME_Y_PAD = (10, 10)  # 'Y' pad around msg frame

    def __init__(self, master, host_id, *args, **kwargs):
        '''
        :param master: The container holding this frame
        :param host_id: Unique id for the host running the application
        '''
        # Initialize frame
        ttk.Frame.__init__(self, master, *args, **kwargs)
        self.host_id = host_id

        # Configure frame's grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=4)
        self.rowconfigure(1, weight=0, pad=ConversationArea._ENTRY_ROW_PAD)

        # MessageFrame for holding the actual messages.
        # NOTE  MessageFrames are only for displaying the messages. All info
        #       relevant to the messages/conversation is tracked elsewhere
        self.msg_display = ma.MessageFrame(self)

        # Entry area for entering a new message
        # TODO Change to Text widget for multiline/non-text
        self.msg_entry = ttk.Entry(self)
        self.msg_entry.bind('<Return>', self.send_message)

        # Send button for sending the content in the message entry
        self.msg_send = ttk.Button(self, text='Send',
                                   command=self.send_message)

        self.msg_send.bind('<Return>', self.send_message)

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

            self.msg_display.add_message('item %d' % i,
                                         sender_id == self.host_id)

    # CALLBACKS
    def send_message(self, event=None):
        msg = self.msg_entry.get().strip()

        # Ignore empty messages
        if msg:
            self.msg_display.add_message(msg, is_host=True)
            self.msg_entry.delete(0, tk.END)  # Clear entry on send
