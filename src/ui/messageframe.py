'''
'''
import config as c
import messagewidget as mw
from scrollableframe import ScrollableFrame
import timeutils
import tkinter as tk


class MessageFrame(ScrollableFrame):
    '''
    UI element derived from ScrollableFrame that displays conversation messages
    '''
    _SENT_X_PAD = (10, 10)  # 'X' pad for sent msg (l-pad, r-pad)
    _SENT_STICKY = tk.EW  # Side for sent messages to appear in msg frame
    _RECV_X_PAD = (10, 10)  # 'X' pad for recv msg (l-pad, r-pad)
    _RECV_STICKY = tk.EW  # Side for received messages to appear in msg frame
    _MSG_Y_PAD = (20, 0)  # 'Y' pad for all msg (t-pad, b-pad)

    host_id = b''  # Universal host ID of the running Endpoint

    def __init__(self, master, name, *args, **kwargs):
        '''
        Initializes the MessageFrame

        :param master: The container holding this frame
        :param name: Friendly name of Endpoint communicating with
        '''
        ScrollableFrame.__init__(self,
                                 master,
                                 mw.MessageWidget.set_visible,
                                 mw.MessageWidget.set_hidden,
                                 *args,
                                 **kwargs)

        self.correspondent_name = name

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
        text_msg = mw.MessageWidget(self.widget_frame, fmt_ts)
        text_msg.set_text(text)

        if ident == c.Config.get(c.ConfigEnum.ENDPOINT_GUID):
            # The host sent this message
            text_msg.set_author('Me', ident, True)
            text_msg.place_message(MessageFrame._SENT_STICKY)

            text_msg.grid(column=0, row=self.num_widgets,
                          sticky=MessageFrame._SENT_STICKY,
                          padx=MessageFrame._SENT_X_PAD,
                          pady=MessageFrame._MSG_Y_PAD)

        else:
            # Someone other than the host sent the message
            text_msg.set_author(self.correspondent_name, ident, False)
            text_msg.place_message(MessageFrame._RECV_STICKY)

            text_msg.grid(column=0, row=self.num_widgets,
                          sticky=MessageFrame._RECV_STICKY,
                          padx=MessageFrame._RECV_X_PAD,
                          pady=MessageFrame._MSG_Y_PAD)

        self.widgets.insert(0, text_msg)
        self.num_widgets += 1
        self._check_visible_widget_range()
        self.scroll_bottom()
