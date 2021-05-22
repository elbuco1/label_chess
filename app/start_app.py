import tkinter as tk
from app.gui import controllers, views, models
import argparse


class ChessAnnotatorApp(tk.Tk):
    """App's entrypoint
    """

    def __init__(self, width=2.5, height=4/7):
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
    args = parser.parse_args()

    models.init_db(clear=args.reset_db)

    app = ChessAnnotatorApp()
    app.mainloop()
