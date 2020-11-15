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
import logging


_g_logger = logging.getLogger(__name__)


class ConversationFrame(ttk.Frame):
    '''UI element displaying relevant information of current conversation'''
    _ENTRY_MAX_LINES = 4  # Max number of lines entry can expand to
    _ENTRY_ROW_PAD = 20  # Padding for row containing msg entry/msg send btn
    _ENTRY_X_PAD = (10, 0)  # 'X' pad for msg entry (l-pad, r-pad)
    _SEND_BTN_X_PAD = (0, 10)  # 'X' pad for send btn (l-pad, r-pad)
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
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=4)
        self.rowconfigure(1, weight=0, pad=ConversationFrame._ENTRY_ROW_PAD)

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

        # Entry area for entering a new message
        self.entry_area = ef.EntryFrame(self,
                                        ConversationFrame._ENTRY_MAX_LINES)
        self.entry_area.bind('<<Send>>', self.__send_text_message)

        # Send button for sending the content in the message entry
        self.send_btn = ttk.Button(self, text='Send',
                                   command=self.__send_text_message)

        self.send_btn.bind('<Return>', self.__send_text_message)

        # Place widgets
        self.entry_area.grid(column=0, row=1,
                             padx=ConversationFrame._ENTRY_X_PAD,
                             sticky=tk.EW)

        self.send_btn.grid(column=1, row=1,
                           padx=ConversationFrame._SEND_BTN_X_PAD,
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

        self.__set_conversation_area_active()

        if self.active_conversation_id:
            self.conversations[self.active_conversation_id].set_inactive()
            self.conversations[self.active_conversation_id].grid_forget()

        # Place the newly active conversation into the UI
        self.conversations[ident].grid(column=0, row=0, columnspan=2,
                                       padx=ConversationFrame._MSG_FRAME_X_PAD,
                                       pady=ConversationFrame._MSG_FRAME_Y_PAD,
                                       sticky=(tk.N, tk.S, tk.E, tk.W))

        self.update_idletasks()  # Wait for UI to update
        self.conversations[ident].set_active()
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
            _g_logger.error('Tried to delete conversation that does not exist')

        if len(self.conversations) == 0:
            self.__set_conversation_area_inactive()

    def report_text_message(self, ident, timestamp, text):
        '''
        Function for passing received message up through UI

        :param ident: GUID of the message sender
        :param timestamp: ISO formatted timestamp
        :param text: Message data
        '''
        self.conversations[ident].add_text_message(ident, timestamp, text)

    def __set_conversation_area_inactive(self):
        self.entry_area.grid_remove()
        self.send_btn.grid_remove()
        self.no_conversation_label.grid(column=0, row=0)

    def __set_conversation_area_active(self):
        self.entry_area.grid()
        self.send_btn.grid()
        self.no_conversation_label.grid_forget()

    # CALLBACKS
    def __send_text_message(self, event=None):
        '''Callback that sends a message in the active conversation'''
        msg_data = self.entry_area.get().strip()

        if self.active_conversation_id and msg_data:
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

        # Keep focus in the message entry
        self.entry_area.focus()
