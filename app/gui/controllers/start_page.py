import tkinter as tk

from app.gui import views, controllers


class StartPageController(base.Controller):

    def __init__(self):
        self.video_height = 115
        self.video_width = 195

        self.pgn_height = 75
        self.pgn_width = 195

        self.annotation_height = 390
        self.annotation_width = 1075

    def bind_view(self, view):
        self.view = view
        self.view.create_view()

        self.view.buttons["video"].configure(
            command=lambda: self.open_window(
                frame=views.VideoDownloaderView,
                controller=controllers.VideoDownloaderController,
                width=self.video_width,
                height=self.video_height
            ))

        self.view.buttons["pgn"].configure(
            command=lambda: self.open_window(
                frame=views.FileDownloaderView,
                controller=controllers.FileDownloaderController,
                width=self.pgn_width,
                height=self.pgn_height
            ))

        self.view.buttons["annotation"].configure(
            command=lambda: self.open_window(
                frame=views.ChessFenAnnotatorView,
                controller=controllers.ChessFenAnnotatorController,
                width=self.annotation_width,
                height=self.annotation_height
            ))

    def open_window(self, frame, controller, width, height):
        window = tk.Toplevel(self.view.master)
        center_window(window, width, height)
        window.grab_set()
        frame = frame(master=window)
        controller = controller()
        controller.bind_view(view=frame)
