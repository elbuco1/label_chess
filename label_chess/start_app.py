#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from label_chess.gui import controllers, views, models
import argparse


class ChessAnnotatorApp(tk.Tk):
    def __init__(self, width=16/7, height=4/7):
        """App's entrypoint

        Args:
            width (float, optional): width of the app's main window is
                width * app's height. Defaults to 16/7.
            height (float, optional): height of the app's main window
                is height * window height. Defaults to 4/7.
        """
        super().__init__()
        controllers.open_window(
            root=self,
            new_view=views.ChessFenAnnotatorView,
            new_controller=controllers.ChessFenAnnotatorController,
            height_ratio=height,
            width_factor=width
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-r', "--reset_db", help='Clear database',
        default=False, action='store_true')
    parser.add_argument(
        '-n', "--no_start", help="Don't start the app.",
        default=False, action='store_true')
    args = parser.parse_args()

    models.init_db(clear=args.reset_db)

    if not args.no_start:
        app = ChessAnnotatorApp()
        app.mainloop()
