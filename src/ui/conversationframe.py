'''
'''
import entryframe as ef
import messageframe as mf
import queue
import timeutils
import datapassing_protocol as dproto
import datapassing
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import logging


_g_logger = logging.getLogger(__name__)


class ConversationFrame(ttk.Frame):
    '''UI element displaying relevant information of current conversation'''
    _ENTRY_MAX_LINES = 4  # Max number of lines entry can expand to
    _ENTRY_X_PAD = (10, 5)  # 'X' pad for msg entry (l-pad, r-pad)
    _ENTRY_Y_PAD = (15, 10)  # 'Y' pad for msg entry (t-pad, b-pad)
    _SEND_BTN_X_PAD = (5, 10)  # 'X' pad for send btn (l-pad, r-pad)
    _SEND_BTN_Y_PAD = (15, 10)  # 'Y' pad for send btn (t-pad, b-pad)
    _MSG_FRAME_X_PAD = (0, 10)  # 'X' pad around msg frame
    _MSG_FRAME_Y_PAD = (0, 0)  # 'Y' pad around msg frame

    def __init__(self, master, host_id, *args, **kwargs):
        '''
        :param master: The container holding this frame
        :param host_id: Unique id for the host running the application
        '''
        # Initialize frame
        ttk.Frame.__init__(self, master, *args, **kwargs)

        self.host_id = host_id
        self.active_conversation_id = b''

        # Configure frame's grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=4)  # Message area
        self.rowconfigure(1, weight=0)  # Entry area/Send button

        # Initialize MessageFrame class with the appropriate host ID
        mf.MessageFrame.host_id = self.host_id

        # Dictionary containing all MessageFrames w/ mapping -> {ident: frame}
        # NOTE  MessageFrames are only for displaying the messages. All info
        #       relevant to the messages/conversation is tracked elsewhere
        self.conversations = {}

        hint_text = 'Select connection to view/send messages'
        self.no_conversation_label = ttk.Label(self,
                                               text=hint_text,
                                               style='EmptyArea.TLabel')

        # Frame containing entry area and send button
        self.bottom_frame = ttk.Frame(self, style='EntryArea.TFrame')
        self.bottom_frame.columnconfigure(0, weight=1)
        self.bottom_frame.columnconfigure(1, weight=0)
        self.bottom_frame.rowconfigure(0, weight=0)
        self.bottom_frame.grid(column=0, row=1, sticky=tk.EW)

        # Entry area for entering a new message
        self.entry_area = ef.EntryFrame(self.bottom_frame,
                                        ConversationFrame._ENTRY_MAX_LINES)

        self.entry_area.bind('<<Send>>', self.__send_text_message)
        self.entry_area.grid(column=0, row=0,
                             padx=ConversationFrame._ENTRY_X_PAD,
                             pady=ConversationFrame._ENTRY_Y_PAD,
                             sticky=tk.EW)

        # Send button for sending the content in the message entry
        self.send_btn = ttk.Button(self.bottom_frame, text='Send',
                                   command=self.__send_text_message)

        self.send_btn.bind('<Return>', self.__send_text_message)
        self.send_btn.grid(column=1, row=0,
                           padx=ConversationFrame._SEND_BTN_X_PAD,
                           pady=ConversationFrame._SEND_BTN_Y_PAD,
                           sticky=tk.W)

        # Implement load previous conversations?
        if len(self.conversations) == 0:
            self.__set_conversation_area_inactive()

    def add_conversation(self, ident, name):
        '''
        :param ident: ID to associate with new conversation
        '''
        self.conversations[ident] = mf.MessageFrame(self, name)

    def activate_conversation(self, ident):
        '''
        :param ident: ID of conversation to activate
        '''
        if ident == self.active_conversation_id:
            return

        try:
            conversation = self.conversations[ident]
        except IndexError:
            # Conversation designated by 'ident' does not exist
            err_msg = 'Tried to activate conversation that does not exist'
            _g_logger.error(err_msg)
            return

        self.__set_conversation_area_active()

        if self.active_conversation_id:
            self.conversations[self.active_conversation_id].set_inactive()
            self.conversations[self.active_conversation_id].grid_forget()

        # Place the newly active conversation into the UI
        conversation.grid(column=0, row=0, columnspan=2,
                          padx=ConversationFrame._MSG_FRAME_X_PAD,
                          pady=ConversationFrame._MSG_FRAME_Y_PAD,
                          sticky=tk.NSEW)

        self.update_idletasks()  # Wait for UI to update
        conversation.set_active()
        self.active_conversation_id = ident

    def remove_conversation(self, ident):
        '''
        :param ident: ID of conversations to delete
        '''
        self.conversations[ident].set_inactive()

        # Remove MessageFrame from UI if it is active
        if ident == self.active_conversation_id:
            self.conversations[ident].grid_forget()
            self.active_conversation_id = b''
            self.__set_conversation_area_inactive()

        # Delete the MessageFrame
        try:
            self.conversations[ident].destroy()
            del self.conversations[ident]
        except IndexError:
            # Conversation designated by 'ident' does not exist
            err_msg = 'Tried to delete conversation that does not exist'
            _g_logger.error(err_msg)

        if len(self.conversations) == 0:
            self.__set_conversation_area_inactive()

    def report_text_message(self, ident, timestamp, text):
        '''
        Function for passing received message up through UI

        :param ident: GUID of the message sender
        :param timestamp: ISO formatted timestamp
        :param text: Message data
        '''
        try:
            self.conversations[ident].add_text_message(ident, timestamp, text)
        except IndexError:
            # Conversation designated by 'ident' does not exist
            err_msg = 'Message reported for conversation that does not exist'
            _g_logger.error(err_msg)

    def __set_conversation_area_inactive(self):
        self.bottom_frame.grid_remove()
        self.no_conversation_label.grid(column=0, row=0)

    def __set_conversation_area_active(self):
        self.bottom_frame.grid()
        self.no_conversation_label.grid_forget()

    # CALLBACKS
    def __send_text_message(self, event=None):
        '''Callback that sends a message in the active conversation'''
        msg_data = self.entry_area.get().strip()

        if not msg_data:
            # Empty message
            messagebox.showinfo('', 'Message is empty')
            return

        if not self.active_conversation_id:
            # No conversation is active
            message_str = 'Must select conversation to send message'
            _g_logger.error(message_str)
            messagebox.showerror('Error', message_str)
            return

        # Construct message to send
        ts = timeutils.get_iso_timestamp()

        dp_msg = dproto.DPTextMsg(dproto.DPMsgDst.DPMSG_DST_BACKEND,
                                  self.active_conversation_id,
                                  ts,
                                  msg_data)

        try:
            # Pass message to the backend
            datapassing.pass_msg(dp_msg)

            # Display
            active_frame = self.conversations[self.active_conversation_id]
            active_frame.add_text_message(self.host_id, ts, msg_data)

            self.entry_area.clear()  # Clear entry on send

        except queue.Full:
            # Message passing queue is full
            _g_logger.error('Failed to push message into sending queue')
            messagebox.showerror('Error', 'Unable to send message')

        # Keep focus in the message entry
        self.entry_area.focus()
