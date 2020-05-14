'''
Module providing service for passing data to and receiving data from the UI
'''
import logging
from shared import datapassing_protocol as dp_proto
import queue
import threading

_g_logger = logging.getLogger(__name__)
_g_SENTINAL = object()  # Object to signal data passing service to stop


def __process_connection_msg(message):
    '''Logic for processing a connection message'''
    mdst = message.destination

    if mdst == dp_proto.DPMsgDst.DPMSG_DST_UI:
        # Pass connection message to UI
        try:
            _g_ui_queue.put_nowait(message)
        except queue.Full:
            _g_logger.error("Unable to pass connection message to UI")

    else:
        _g_logger.error("Message had invalid destination")


def __process_text_msg(message):
    '''Logic for processing a text message'''
    mdst = message.destination

    if mdst == dp_proto.DPMsgDst.DPMSG_DST_UI:
        # Pass text message to UI
        try:
            _g_ui_queue.put_nowait(message)
        except queue.Full:
            _g_logger.error("Unable to pass text message to UI")

    elif mdst == dp_proto.DPMsgDst.DPMSG_DST_BACKEND:
        # TODO Pass text message to Backend
        pass

    else:
        _g_logger.error("Message had invalid destination")


def __process_msg(message):
    '''Logic for processing a queue message'''
    mtype = message.msg_type

    if mtype == dp_proto.DPMsgType.DPMSG_TYPE_CONNECTION:
        __process_connection_msg(message)

    elif mtype == dp_proto.DPMsgType.DPMSG_TYPE_TEXT_MSG:
        __process_text_msg(message)

    else:
        _g_logger.error("Message had invalid type")


def __mainloop():
    '''Processing loop for the data passing service'''
    done = False

    while not done:
        # Wait for messages to be queued
        qmsg = _g_msg_queue.get()

        if qmsg is _g_SENTINAL:
            # Kill signal received
            done = True

        else:
            __process_msg(qmsg)

    _g_logger.info("Data passing service stopped")


def pass_msg(message):
    '''Function for passing a message'''
    try:
        _g_msg_queue.put_nowait()
    except queue.Full:
        _g_logger.error("Unable to queue message")


def start(ui_queue):
    '''Starts service that allows passing data between the UI and backend'''
    global _g_msg_queue  # Queue for data passing messages
    global _g_thread     # Thread service is running on
    global _g_ui_queue   # Queue for passing data to the UI

    # Initialize the message queues
    _g_msg_queue = queue.Queue()
    _g_ui_queue = ui_queue

    # Initialize and start the thread for the service to run on
    _g_thread = threading.Thread(target=__mainloop)
    _g_thread.start()

    _g_logger.info("Data passing service started")


def kill():
    '''Stops the data passing service's thread'''
    _g_logger.info("Data passing service received kill signal")

    try:
        _g_msg_queue.put_nowait(_g_SENTINAL)
    except queue.Full:
        _g_logger.error("Unable to kill data passing service")
