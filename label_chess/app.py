#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from label_chess import controllers, views


class ChessAnnotatorApp(tk.Tk):
    def __init__(self, width=16/7, height=2/3):
        """App's entrypoint

        Args:
            width (float, optional): width of the app's main window is
                width * app's height. Defaults to 16/7.
            height (float, optional): height of the app's main window
                is height * window height. Defaults to 2/3.
        """
        super().__init__()
        controllers.open_window(
            root=self,
            new_view=views.ChessFenAnnotatorView,
            new_controller=controllers.ChessFenAnnotatorController,
            height_ratio=height,
            width_factor=width
        )
