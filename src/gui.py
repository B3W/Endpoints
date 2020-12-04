'''"Frontend" for Endpoints application'''
import logging
import tkinter as tk
import appui


def start(in_q):
    '''
    :param in_q: Queue for data coming from backend to GUI
    '''
    logger = logging.getLogger(__name__)  # Retrieve module logger

    # Run UI
    root = tk.Tk()
    icon = tk.PhotoImage(file='assets/Endpoints-Icon-3-16x16.png')
    root.image = icon
    root.iconphoto(True, icon)

    gui = appui.EndpointUI(root, in_q)

    logger.debug('Opening UI...')

    gui.mainloop()

    logger.debug('UI Closed')
