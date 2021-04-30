import tkinter as tk
from .base import View


class VideoDownloaderView(View):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.minsize = 25

        self.resolutions = ["1080p",
                            "720p",
                            "480p",
                            "360p"]
        self.entries = {}
        self.buttons = {}
        self.string_vars = {}

        self.config_window()

    def create_view(self):
        """Create all app's widgets
        """
        # URL entry
        frm_label = "URL"
        self.frm_url = self.create_label_frame(frm_label)
        self.entries[frm_label] = tk.Entry(
            self.frm_url)
        self.entries[frm_label].grid(row=0, column=0, sticky="nsew")
        self.frm_url.grid(row=0, column=0, sticky="nsew")

        # Resolution option menu
        frm_label = "Resolution"
        self.frm_res = self.create_label_frame(frm_label)
        self.string_vars[frm_label] = tk.StringVar(self)
        self.res_menu = tk.OptionMenu(
            self.frm_res,
            self.string_vars[frm_label],
            *self.resolutions
        )
        self.res_menu.grid(row=0, column=0, sticky="nsew")
        self.frm_res.grid(row=1, column=0,
                          sticky="nsew")

        # Download menu
        btn_name = "Download"
        self.buttons[btn_name] = tk.Button(self, text=btn_name)
        self.buttons[btn_name].grid(row=2, column=0, sticky="nsew")

    def create_label_frame(self, text):
        frm = tk.LabelFrame(self, text=text)
        frm.rowconfigure(0, weight=1)
        frm.columnconfigure(0, weight=1)
        return frm

    def config_window(self):
        """Configure app's root node (tk.Tk()) i.e. self
        """
        self.rowconfigure(0, minsize=self.minsize, weight=1)
        self.columnconfigure(0, minsize=self.minsize, weight=1)
        self.grid(row=0, column=0, sticky="nsew")
        self.master.title("Youtube video downloader")


class FileDownloaderView(View):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.minsize = 25

        self.entries = {}
        self.buttons = {}

        self.config_window()

    def create_view(self):
        """Create all app's widgets
        """
        # URL entry
        frm_label = "URL"
        self.frm_url = tk.LabelFrame(self, text=frm_label)
        self.entries[frm_label] = tk.Entry(self.frm_url)
        self.entries[frm_label].grid(row=0, column=0, sticky="nsew")
        self.frm_url.grid(row=0, column=0, sticky="nsew")

        # Download menu
        btn_name = "Download"
        self.buttons[btn_name] = tk.Button(self, text=btn_name)
        self.buttons[btn_name].grid(row=1, column=0, sticky="nsew")

    def config_window(self):
        """Configure app's root node (tk.Tk()) i.e., self
        """
        self.rowconfigure(0, minsize=self.minsize, weight=1)
        self.columnconfigure(0, minsize=self.minsize, weight=1)
        self.grid(row=0, column=0, sticky="nsew")
        self.master.title("PGN downloader")
