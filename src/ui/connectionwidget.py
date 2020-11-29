import tkinter as tk
from tkinter import ttk


class ConnectionWidget(ttk.Frame):
    _BINDTAG = 'ConnectionWidget'

    def __init__(self, master, guid, name, *args, **kwargs):
        '''
        Override of ttk.Frame's initialization function

        :param master: Widget's master
        '''
        # Initialize root widget
        ttk.Frame.__init__(self, master,
                           style='ConnectionWidget.TFrame',
                           *args, **kwargs)

        self.columnconfigure(0, weight=1)  # Name label
        self.columnconfigure(1, weight=0)  # Notification icon
        self.rowconfigure(0, weight=0)

        self.guid = guid
        self.name = name
        self.selected = False
        self.notify_pending = True

        # Add custom bindtag for click event
        btags = (ConnectionWidget._BINDTAG,) + self.bindtags()
        self.bindtags(btags)

        # Initialize label that holds the connection's name
        self.name_lbl = ttk.Label(self,
                                  text=self.name,
                                  style='ConnectionWidget.TLabel')
        self.name_lbl.grid(column=0, row=0, sticky=tk.EW)

        # Add custom bindtag for click event
        btags = (ConnectionWidget._BINDTAG,) + self.name_lbl.bindtags()
        self.name_lbl.bindtags(btags)

        # Load notification icon
        notify_image_path = 'assets/Unread-Notification-16x16.png'
        notify_image = tk.PhotoImage(file=notify_image_path)

        # Initialize label for holding notification icon
        self.notify_lbl = ttk.Label(self,
                                    image=notify_image,
                                    style='ConnectionWidget.TLabel')
        self.notify_lbl.image = notify_image  # Keep reference to image
        self.notify_lbl.grid(column=1, row=0)
        self.notify_lbl.grid_remove()

        # Add custom bindtag for click event
        btags = (ConnectionWidget._BINDTAG,) + self.notify_lbl.bindtags()
        self.notify_lbl.bindtags(btags)

        # Bind callback for click event to custom bindtag
        self.bind_class(ConnectionWidget._BINDTAG,
                        '<Button-1>',
                        self.__click_callback)

        # Enter/Leave events only need to bind to outermost container (frame)
        self.bind('<Enter>', self.__hover_enter)
        self.bind('<Leave>', self.__hover_exit)

    def select(self, event=None):
        self.selected = True
        self.configure(style='Selected.ConnectionWidget.TFrame')
        self.name_lbl.configure(style='Selected.ConnectionWidget.TLabel')
        self.notify_lbl.configure(style='Selected.ConnectionWidget.TLabel')

        if self.notify_pending:
            self.notify_pending = False
            self.notify_lbl.grid_remove()

    def deselect(self):
        self.selected = False
        self.configure(background='white')

    def notify(self):
        if self.selected:
            return

        self.notify_pending = True
        self.notify_lbl.grid()

    # CALLBACKS
    def __click_callback(self, event):
        self.event_generate('<<ItemSelect>>')
        return 'break'

    def __hover_enter(self, event):
        if not self.selected:
            frame_style = 'Selected.ConnectionWidget.TFrame'
            label_style = 'Selected.ConnectionWidget.TLabel'

            self.configure(style=frame_style)
            self.name_lbl.configure(style=label_style)
            self.notify_lbl.configure(style=label_style)

    def __hover_exit(self, event):
        if not self.selected:
            frame_style = 'Unselected.ConnectionWidget.TFrame'
            label_style = 'Unselected.ConnectionWidget.TLabel'

            self.configure(style=frame_style)
            self.name_lbl.configure(style=label_style)
            self.notify_lbl.configure(style=label_style)
