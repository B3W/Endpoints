'''"Frontend" for Endpoints application'''
import logging
import tkinter as tk
import appui


def start(host_guid, in_q, out_q):
    '''
    :param in_q: Queue for data coming from backend to GUI
    :param out_q: Queue for passing data to backend from GUI
    '''
    logger = logging.getLogger(__name__)  # Retrieve module logger

    # Run UI
    root = tk.Tk()
    gui = appui.EndpointUI(root, host_guid, in_q, out_q)

    logger.info('Opening UI...')

    gui.mainloop()

    logger.info('UI Closed')
