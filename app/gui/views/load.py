import tkinter as tk
from app.gui.base import View


class VideoLoaderView(View):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master

        self.entries = {}
        self.buttons = {}
        self.labels = {}

        self.config_window()

    def create_view(self):
        """Create all app's widgets
        """
        self.buttons["select_video"] = tk.Button(self, text="Select video")
        self.buttons["select_video"].grid(row=0, column=0, sticky="nsew")

        self.labels["select_video"] = tk.Label(self)
        self.labels["select_video"].grid(row=1, column=0, sticky="nsew")

        # URL entry
        frm_label = "URL (optional)"
        self.frm_url = self.create_label_frame(frm_label)
        self.entries["URL"] = tk.Entry(
            self.frm_url)
        self.entries["URL"].grid(row=0, column=0, sticky="nsew")
        self.frm_url.grid(row=2, column=0, sticky="nsew")

        # Add button
        self.buttons["Add"] = tk.Button(self, text="Add")
        self.buttons["Add"].grid(row=3, column=0, sticky="nsew")

    def create_label_frame(self, text):
        frm = tk.LabelFrame(self, text=text)
        frm.columnconfigure(0, weight=1)
        return frm

    def config_window(self):
        """Configure app's root node (tk.Tk()) i.e. self
        """
        # resizable window
        self.master.resizable(width=True, height=False)
        self.master.rowconfigure(0,  weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.title("Add video to database")

        self.columnconfigure(0, weight=1)
        self.rowconfigure([0, 1, 2, 3], weight=1)
        self.grid(row=0, column=0, sticky="nsew")


class PGNLoaderView(View):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master

        self.entries = {}
        self.buttons = {}
        self.labels = {}

        self.config_window()

    def create_view(self):
        """Create all app's widgets
        """

        self.buttons["select_pgn"] = tk.Button(self, text="Select PGN")
        self.buttons["select_pgn"].grid(row=0, column=0, sticky="nsew")

        self.labels["select_pgn"] = tk.Label(self)
        self.labels["select_pgn"].grid(row=1, column=0, sticky="nsew")

        # URL entry
        frm_label = "URL (optional)"
        self.frm_url = tk.LabelFrame(self, text=frm_label)
        self.frm_url.columnconfigure(0, weight=1)
        self.entries["URL"] = tk.Entry(self.frm_url)
        self.entries["URL"].grid(row=0, column=0, sticky="nsew")
        self.frm_url.grid(row=2, column=0, sticky="nsew")

        # Download menu
        self.buttons["Add"] = tk.Button(self, text="Add")
        self.buttons["Add"].grid(row=3, column=0, sticky="nsew")

    def config_window(self):
        """Configure app's root node (tk.Tk()) i.e., self
        """
        # resizable window
        self.master.resizable(width=True, height=False)
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.title("Add PGN to database")
        # resizable view
        self.columnconfigure(0, weight=1)
        self.rowconfigure([0, 1, 2, 3], weight=1)
        self.grid(row=0, column=0, sticky="nsew")
