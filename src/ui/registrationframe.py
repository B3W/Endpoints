import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
import resizabletext as rt
import config as c
from version import __version__


class RegistrationFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        # Initialize the instance
        ttk.Frame.__init__(self, master, *args, **kwargs)

        self.master.title('Setup')
        self.master.protocol('WM_DELETE_WINDOW', self.__close)
        self.master.minsize(width=500, height=300)
        self.master.resizable(False, False)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        # Configure styles
        welcome_title_font = Font(family="Ariel", size=20, underline=True)
        welcome_text_font = Font(family="Ariel", size=12)
        char_count_font = Font(family="Ariel", size=8)

        style = ttk.Style()

        style.configure('WelcomeWindowTitle.TLabel',
                        anchor=tk.CENTER,
                        font=welcome_title_font)

        style.configure('WelcomeWindow.TLabel', font=welcome_text_font)
        style.configure('WelcomeWindow.TEntry', font=welcome_text_font)
        style.configure('CharacterCount.TLabel', font=char_count_font)

        # First page of the welcome window
        self.page_one = RegistrationPageOne(self, welcome_text_font)
        self.page_one.grid(column=0, row=0, sticky=tk.NSEW)

        # Second page of welcome window
        self.page_two = RegistrationPageTwo(self)
        self.page_two.grid(column=0, row=0)
        self.page_two.grid_remove()

        # Final page of the welcome window
        self.final_page = RegistrationFinalPage(self, welcome_text_font)
        self.final_page.grid(column=0, row=0)
        self.final_page.grid_remove()

        self.current_page = self.page_one

        # Button for going to next page in welcome sequence
        self.next_btn = ttk.Button(self, text='Next',
                                   command=lambda: self.__next())

        self.next_btn.grid(column=0, row=1, pady=(10, 10), sticky=tk.S)

        self.next_btn.focus_set()
        self.next_btn.bind('<Return>', self.__next)

        # Place window in the center of the screen
        self.master.update_idletasks()
        w = self.master.winfo_width()
        h = self.master.winfo_height()
        wscreen = self.winfo_screenwidth()
        hscreen = self.winfo_screenheight()

        x = (wscreen / 2) - (w / 2)
        y = (hscreen / 2) - (h / 2)

        self.master.geometry(f'{int(w)}x{int(h)}+{int(x)}+{int(y)}')

    def __next(self, event=None):
        if self.current_page == self.page_one:
            # Switch to the entry page
            self.current_page.grid_remove()
            self.page_two.grid()
            self.current_page = self.page_two

        elif self.current_page == self.page_two:
            # Collect users input and write it to the configuration
            user_input = self.page_two.username.get().strip()

            if len(user_input) > 0:
                c.Config.set(c.ConfigEnum.ENDPOINT_NAME, user_input)

                # Set user as registered in config
                c.Config.set(c.ConfigEnum.NEW_USER, False)

                # Switch to the confirmation page
                self.current_page.grid_remove()
                self.final_page.set_user(user_input)
                self.final_page.grid()
                self.current_page = self.final_page

                # Change text of the 'next' button
                self.next_btn.configure(text='Close')

        else:
            self.master.destroy()

    def __close(self, event=None):
        if self.current_page == self.final_page:
            self.master.destroy()

    @staticmethod
    def show():
        """
        Shows the register user window and blocks until it is closed
        """
        root = tk.Tk()
        registration = RegistrationFrame(root)
        registration.pack(fill=tk.BOTH, expand=True)

        root.mainloop()


class RegistrationPageOne(ttk.Frame):
    def __init__(self, master, font, *args, **kwargs):
        # Initialize the instance
        ttk.Frame.__init__(self, master, *args, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)

        # Label containing title message
        self.welcome_title = ttk.Label(self,
                                       text='Welcome!',
                                       style='WelcomeWindowTitle.TLabel')

        self.welcome_title.grid(column=0, row=0, pady=(5, 5), sticky=tk.EW)

        # Text containing welcome message
        welcome_msg_str = f'Thank you for using Endpoints v{__version__}!\n\n'\
                          'Endpoints is a simple chat app that allows you to' \
                          ' message other devices running Endpoints connected'\
                          ' to the same subnet as you.\n\n'                   \
                          'Please follow the one-step setup to get started.'

        self.welcome_text = rt.ResizableText(self,
                                             relief=tk.FLAT,
                                             wrap=tk.WORD,
                                             bg='gray95',
                                             font=font)
        self.welcome_text.insert(tk.END, welcome_msg_str)
        self.welcome_text.config(state=tk.DISABLED)
        self.welcome_text.grid(column=0, row=1, padx=(15, 15), sticky=tk.NSEW)


class RegistrationPageTwo(ttk.Frame):
    _MAX_USERNAME_CHARACTERS = 40

    def __init__(self, master, *args, **kwargs):
        # Initialize the instance
        ttk.Frame.__init__(self, master, *args, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)  # Label
        self.rowconfigure(1, weight=0)  # Entry
        self.rowconfigure(2, weight=0)  # Label

        # Label containing hint text
        hint_str = 'Enter username:\n' \
                   '(what you will be identified as to other Endpoints)'
        self.hint_lbl = ttk.Label(self,
                                  text=hint_str,
                                  style='WelcomeWindow.TLabel')

        self.hint_lbl.grid(column=0, row=0,
                           padx=(15, 15), pady=(5, 5), sticky=tk.EW)

        # Label for tracking character count
        self.char_cnt = tk.StringVar()
        self.char_cnt.set(f'0/{RegistrationPageTwo._MAX_USERNAME_CHARACTERS}')
        self.count_lbl = ttk.Label(self,
                                   textvariable=self.char_cnt,
                                   style='CharacterCount.TLabel')

        self.count_lbl.grid(column=0, row=2, padx=(15, 15), sticky=tk.NE)

        # Widget for entering username
        validatation_wrapper = (self.register(self.__validate), '%P')

        self.username = tk.StringVar()
        self.username.trace_add('write', self.__update_character_count)
        self.entry = ttk.Entry(self,
                               textvariable=self.username,
                               validate='key',
                               validatecommand=validatation_wrapper,
                               style='WelcomeWindow.TEntry')

        self.entry.grid(column=0, row=1, padx=(15, 15), sticky=tk.EW)

    def __update_character_count(self, index, value, mode):
        cnt = len(self.username.get())
        new_str = f'{cnt}/{RegistrationPageTwo._MAX_USERNAME_CHARACTERS}'
        self.char_cnt.set(new_str)

    def __validate(self, username):
        return len(username) <= RegistrationPageTwo._MAX_USERNAME_CHARACTERS


class RegistrationFinalPage(ttk.Frame):
    def __init__(self, master, font, *args, **kwargs):
        # Initialize the instance
        ttk.Frame.__init__(self, master, *args, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)

        # Label containing title message
        self.complete_title = ttk.Label(self,
                                        text='Registration Complete!',
                                        style='WelcomeWindowTitle.TLabel')

        self.complete_title.grid(column=0, row=0, pady=(5, 5), sticky=tk.EW)

        # Text containing completion message
        self.complete_text = rt.ResizableText(self,
                                              relief=tk.FLAT,
                                              wrap=tk.WORD,
                                              bg='gray95',
                                              font=font)

        self.complete_text.grid(column=0, row=1, padx=(15, 15), sticky=tk.NSEW)

    def set_user(self, username):
        complete_msg_str = f'Enjoy Endpoints, {username}!'

        self.complete_text.insert(tk.END, complete_msg_str)
        self.complete_text.config(state=tk.DISABLED)
