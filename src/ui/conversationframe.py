'''
'''
import messageframe as mf
import queue
import timeutils
import datapassing_protocol as dproto
import tkinter as tk
from tkinter import ttk


class ConversationFrame(ttk.Frame):
    '''UI element displaying relevant information of current conversation'''
    _ENTRY_ROW_PAD = 20  # Padding for row containing msg entry/msg send btn
    _ENTRY_X_PAD = (10, 0)  # 'X' pad for msg entry (l-pad, r-pad)
    _SEND_BTN_X_PAD = (0, 10)  # 'X' pad for send btn (l-pad, r-pad)
    _MSG_FRAME_X_PAD = (0, 10)  # 'X' pad around msg frame
    _MSG_FRAME_Y_PAD = (10, 10)  # 'Y' pad around msg frame

    def __init__(self, master, host_id, send_q, *args, **kwargs):
        '''
        :param master: The container holding this frame
        :param host_id: Unique id for the host running the application
        '''
        # Configure Style
        style = ttk.Style()
        style.configure('tmp.TFrame', background='red')
        style.configure('timestamp.TLabel',
                        foreground='grey',
                        font='Helvetica 8 italic')

        # Initialize frame
        ttk.Frame.__init__(self, master, *args, **kwargs)

        self.host_id = host_id
        self.send_q = send_q
        self.active_conversation = b''

        # Configure frame's grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=4)
        self.rowconfigure(1, weight=0, pad=ConversationFrame._ENTRY_ROW_PAD)

        # Initialize MessageFrame class with the appropriate host ID
        mf.MessageFrame.host_id = self.host_id

        # Dictionary containing all MessageFrames w/ mapping -> {ident: frame}
        # NOTE  MessageFrames are only for displaying the messages. All info
        #       relevant to the messages/conversation is tracked elsewhere
        self.conversations = {}

        # Entry area for entering a new message
        # TODO Change to Text widget for multiline/non-text
        self.msg_entry = ttk.Entry(self)
        self.msg_entry.bind('<Return>', self.__send_text_message)

        # Send button for sending the content in the message entry
        self.msg_send = ttk.Button(self, text='Send',
                                   command=self.__send_text_message)

        self.msg_send.bind('<Return>', self.__send_text_message)

        # Place widgets
        self.msg_entry.grid(column=0, row=1,
                            padx=ConversationFrame._ENTRY_X_PAD,
                            sticky=(tk.E, tk.W))

        self.msg_send.grid(column=1, row=1,
                           padx=ConversationFrame._SEND_BTN_X_PAD,
                           sticky=(tk.W,))

    def add_conversation(self, ident):
        '''
        :param ident: ID to associate with new conversation
        '''
        self.conversations[ident] = mf.MessageFrame(self)

    def activate_conversation(self, ident):
        '''
        :param ident: ID of conversation to activate
        '''
        if ident == self.active_conversation:
            return

        if self.active_conversation:
            self.conversations[self.active_conversation].grid_forget()

        # Place the newly active conversation into the UI
        ConversationFrame.__place_message_frame(self.conversations[ident])
        self.active_conversation = ident

    def remove_conversation(self, ident):
        '''
        :param ident: ID of conversations to delete
        '''
        # Remove MessageFrame from UI if it is active
        if ident == self.active_conversation:
            self.conversations[ident].grid_forget()
            self.active_conversation = b''

        # Delete the MessageFrame
        self.conversations[ident].destroy()
        del self.conversations[ident]

    def report_text_message(self, ident, timestamp, text):
        '''
        '''
        self.conversations[ident].add_text_message(ident, timestamp, text)

    def __place_message_frame(frame):
        '''
        '''
        frame.grid(column=0, row=0, columnspan=2,
                   padx=ConversationFrame._MSG_FRAME_X_PAD,
                   pady=ConversationFrame._MSG_FRAME_Y_PAD,
                   sticky=(tk.N, tk.S, tk.E, tk.W))

    # CALLBACKS
    def __send_text_message(self, event=None):
        msg = self.msg_entry.get().strip()

        if self.active_conversation and msg:
            # Construct message to send
            ts = timeutils.get_timestamp()

            msg = dproto.DPTextMsg(dproto.DPMsgDst.DPMSG_DST_BACKEND,
                                   self.host_id,
                                   ts,
                                   msg)

            try:
                # Push into sending queue
                self.send_q.put_nowait(msg)

                # Display
                fmt_ts = timeutils.format_timestamp(ts)

                active_frame = self.conversations[self.active_conversation]
                active_frame.add_text_message(self.host_id, fmt_ts, msg)

                self.msg_entry.delete(0, tk.END)  # Clear entry on send

            except queue.Full:
                print('Failed to push message into sending queue')
