#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk

from label_chess.base import View


class LoaderView(View):
    def __init__(self, master=None, add_name="", height=0):
        """Subclass tkinter.Frame. Displays vertically:
        * a button labeled "select_<add_name>"
        * a label
        * an entry labeled "URL (optional)
        * a button labeled "Add"

        It is intended to select a file on disk (video, txt),
        join an optional attribute and save it to database.

        This class implements only the front end, no logic should
        be implemented here.

        Args:
            master (tk.Frame/tk.Tk, tk.TopLevel, optional): the widget's parent.
                Defaults to None.
            add_name (str, optional): string to customize the text of the first button.
                Button is named "select_<add_name>". Defaults to "".
            height (int, optional): The height of the window. For compatibility reasons,
                not used here. Defaults to 0.
        """
        super().__init__(master)
        self.master = master
        self.height = height
        self.add_name = add_name

        # widgets are stored in one dict
        # per widget type
        self.entries = {}
        self.buttons = {}
        self.labels = {}

        self.config_window()

    def create_view(self):
        """Create all frame's widgets
        """
        select_key = f"select_{self.add_name}"
        self.buttons[select_key] = tk.Button(
            self, text=f"Select {self.add_name}")
        self.buttons[select_key].grid(row=0, column=0, sticky="nsew")

        self.labels[select_key] = tk.Label(self)
        self.labels[select_key].grid(row=1, column=0, sticky="nsew")

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
        """Configure master and self.
        """
        # resizable window
        self.master.resizable(width=True, height=False)
        self.master.rowconfigure(0,  weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.title(f"Add {self.add_name} to database")

        self.columnconfigure(0, weight=1)
        self.rowconfigure([0, 1, 2, 3], weight=1)
        self.grid(row=0, column=0, sticky="nsew")


class VideoLoaderView(LoaderView):
    def __init__(self, master=None, height=0):
        """Inherits from LoaderView and fix the
        value of the add_name argument to "video".
        """
        super().__init__(master=master, add_name="video")


class PGNLoaderView(LoaderView):
    def __init__(self, master=None, height=0):
        """Inherits from LoaderView and fix the
        value of the add_name argument to "pgn".
        """
        super().__init__(master=master, add_name="pgn")
