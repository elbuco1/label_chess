import tkinter as tk

from .base import Controller
from chlabel.gui import views, controllers


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


class StartPageController(Controller):

    def __init__(self):
        self.video_height = 1/8
        self.video_width = 2.2

        self.pgn_height = 1/12
        self.pgn_width = 3

        self.annotation_height = 3/7
        self.annotation_width = 3

    def bind_view(self, view):
        """Bind buttons to open new windows
        """
        self.view = view
        self.view.create_view()

        self.view.buttons["video"].configure(
            command=lambda: self.open_window(
                view=views.VideoDownloaderView,
                controller=controllers.VideoDownloaderController,
                width_factor=self.video_width,
                height_ratio=self.video_height
            ))

        self.view.buttons["pgn"].configure(
            command=lambda: self.open_window(
                view=views.FileDownloaderView,
                controller=controllers.FileDownloaderController,
                width_factor=self.pgn_width,
                height_ratio=self.pgn_height
            ))

        self.view.buttons["annotation"].configure(
            command=lambda: self.open_window(
                view=views.ChessFenAnnotatorView,
                controller=controllers.ChessFenAnnotatorController,
                width_factor=self.annotation_width,
                height_ratio=self.annotation_height
            ))

    def open_window(self, view, controller, height_ratio, width_factor):
        """ Open a window from top window
        """
        # create new window from root Tk object
        window = tk.Toplevel(self.view.master)
        # height is a proportion of the screen
        height = int(window.winfo_screenheight() * height_ratio)
        # width is height multiplied by a factor
        width = int(height * width_factor)
        # center new window on screen
        center_window(window, width, height)
        # redirect keyboard to new window
        window.grab_set()
        # create and bind view and controller
        view = view(master=window)
        controller = controller()
        controller.bind_view(view=view)
