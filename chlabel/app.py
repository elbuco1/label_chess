import tkinter as tk
from chlabel.gui import controllers, views


class ChessAnnotatorApp(tk.Tk):
    """App's entrypoint
    """

    def __init__(self, width=178, height=103):
        super().__init__()
        frame = views.StartPageView(master=self)
        controller = controllers.StartPageController()
        controller.bind_view(frame)

        controllers.center_window(self, width, height)


if __name__ == "__main__":
    app = ChessAnnotatorApp()
    app.mainloop()
