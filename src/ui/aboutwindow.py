import tkinter as tk
from tkinter import ttk
from version import __version__


class AboutWindow(tk.Toplevel):
    def __init__(self, master, *args, **kwargs):
        # Initialize the toplevel instance
        tk.Toplevel.__init__(self, master, *args, **kwargs)
        self.title('About')
        self.protocol('WM_DELETE_WINDOW', self.close)
        self.minsize(width=200, height=100)

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)
        self.resizable(False, False)

        # Label containing icon
        icon_image_path = 'assets/Endpoints-Icon-64x64.png'
        icon_image = tk.PhotoImage(file=icon_image_path)
        self.icon_lbl = ttk.Label(self, image=icon_image)
        self.icon_lbl.image = icon_image  # Hold reference to image
        self.icon_lbl.grid(column=0, row=0, sticky=tk.N)

        # Label containing app's name/version
        version_str = f'v{__version__}'
        self.app_lbl = ttk.Label(self,
                                 text=f'Endpoints {version_str}',
                                 style='AboutMain.TLabel')
        self.app_lbl.grid(column=1, row=0, padx=(0, 10), sticky=tk.W)

        # Button for closing the window
        self.close_btn = ttk.Button(self,
                                    text='Ok',
                                    command=lambda: self.close())
        self.close_btn.grid(column=0, row=2, columnspan=2,
                            pady=(10, 10), sticky=tk.S)

        self.close_btn.focus_set()
        self.close_btn.bind('<Return>', self.close)

        # Find center of root window
        root_x = self.master.winfo_rootx()
        root_y = self.master.winfo_rooty()
        root_w = self.master.winfo_width()
        root_h = self.master.winfo_height()
        root_center_x = root_x + (root_w / 2)
        root_center_y = root_y + (root_h / 2)

        # Place in the middle of the root window
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = root_center_x - (w / 2)
        y = root_center_y - (h / 2)

        self.geometry(f'{int(w)}x{int(h)}+{int(x)}+{int(y)}')

        # Configure toplevel instance for 'application modal' usage
        self.transient(master)  # This window related to master widget
        self.wait_visibility()  # Cannot grab until window appears
        self.grab_set()  # Ensure all input goes to this

    def close(self, event=None):
        self.grab_release()
        self.destroy()
