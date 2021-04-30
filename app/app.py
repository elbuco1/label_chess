import tkinter as tk
from app.gui import controllers, views


def center_window(win, width, height):
    """Display a tkinter window at the center
    of the screen.

    Args:
        win (tk.Tk): window
        width (int): window width
        height ([type]): window height
    """
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()

    pos_x = int((screen_width-width)/2)
    pos_y = int((screen_height-height)/2)

    win.geometry(f"{width}x{height}+{pos_x}+{pos_y}")


class ChessAnnotatorApp(tk.Tk):
    """App's entrypoint
    """

    def __init__(self, width=178, height=103):
        super().__init__()
        frame = views.StartPageView(master=self)
        controller = controllers.StartPageController()
        controller.bind_view(frame)

        center_window(self, width, height)


if __name__ == "__main__":
    app = ChessAnnotatorApp()
    app.mainloop()
