import tkinter as tk
from chlabel.gui import controllers, views


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
    app = ChessAnnotatorApp()
    app.mainloop()
