import tkinter as tk


class ConnectionWidget(tk.Button):
    def __init__(self, master, guid, name, *args, **kwargs):
        '''
        Override of tk.Text's initialization function

        :param master: Widget's master
        '''
        # Initialize root widget
        tk.Button.__init__(self, master,
                           text=name,
                           anchor=tk.W,
                           compound=tk.RIGHT,
                           relief=tk.FLAT,
                           background='white',
                           padx=5,
                           pady=5,
                           *args, **kwargs)

        self.guid = guid
        self.name = name
        self.selected = False
        self.notify_pending = True
        self.notify_image = None

        self.bind('<Button-1>', self.__click_callback)
        self.bind('<Enter>', self.__hover_enter)
        self.bind('<Leave>', self.__hover_exit)

    def select(self, event=None):
        self.selected = True
        self.configure(background='light sky blue')

        if self.notify_pending:
            self.notify_pending = False
            self.notify_image = None
            self.configure(image='')

    def deselect(self):
        self.selected = False
        self.configure(background='white')

    def notify(self):
        if self.selected:
            return

        self.notify_pending = True
        notify_image_path = 'assets/Unread-Notification-16x16.png'
        self.notify_image = tk.PhotoImage(file=notify_image_path)
        self.configure(image=self.notify_image)

    # CALLBACKS
    def __click_callback(self, event):
        self.event_generate('<<ItemSelect>>')
        return 'break'

    def __hover_enter(self, event):
        if not self.selected:
            self.configure(background='light sky blue')

    def __hover_exit(self, event):
        if not self.selected:
            self.configure(background='white')
