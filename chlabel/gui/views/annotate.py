import tkinter as tk
from PIL import Image, ImageTk

from .base import View
from chlabel import utils, chess2fen


class ChessFenAnnotatorView(View):
    def __init__(self, master=None, chess_img_height=340):
        super().__init__(master)
        self.master = master
        self.chess_img_height = chess_img_height
        self.config_window()

        self.frames = {}

    def create_view(self):
        self.frames["side_menu"] = SideMenuFrame(self)
        self.frames["side_menu"].create_view()
        self.frames["side_menu"].grid(row=0, column=0, sticky="nsew")

        self.frames["video"] = VideoFrame(self,
                                          chess_img_height=self.chess_img_height)
        self.frames["video"].create_view()
        self.frames["video"].grid(row=0, column=1, sticky="nsew")

        self.frames["pgn"] = PGNFrame(self,
                                      img_height=self.chess_img_height)
        self.frames["pgn"].create_view()
        self.frames["pgn"].grid(row=0, column=2, sticky="nsew")

    def config_window(self):
        """Configure app's root node (tk.Tk()) i.e. self
        """
        self.master.resizable(False, False)
        # self.rowconfigure(0,  weight=1)
        # self.columnconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky="nsew")
        self.master.title("Chess video FEN annotator")


class PGNFrame(tk.Frame):
    def __init__(self, master=None, img_height=320):
        super().__init__(master)
        self.master = master
        self.img_height = img_height

        self.buttons = {}
        self.labels = {}
        self.config_window()

    def create_view(self):
        # Label frame container
        self.container = tk.LabelFrame(master=self, text="Positions")
        self.container.rowconfigure(0,  weight=1)
        self.container.columnconfigure(0, weight=1)
        self.container.grid(row=0, column=0, sticky="nsew")

        # chess fen
        self.labels["fen"] = tk.Label(
            master=self.container)
        self.labels["fen"].grid(row=0, column=0, sticky="nsew")
        self.set_image(chess2fen.create_empty_board())

        # skip fen button
        self.buttons["skip_fen"] = tk.Button(
            master=self.container,
            text="Skip(Space)",
            state="disabled")
        self.buttons["skip_fen"].grid(row=2, column=0, sticky="ew")

    def config_window(self):
        """Configure app's root node (tk.Tk()) i.e. self
        """
        self.rowconfigure(0,  weight=1)
        self.columnconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky="nsew")

    def set_image(self, image):
        """Take a PIL image and resize it
        according to a specified height.
        Display the image in the video frame.

        Args:
            image (PIL.Image)
        """
        image = image.resize((self.img_height, self.img_height))
        image = ImageTk.PhotoImage(image)
        self.labels["fen"].configure(image=image)
        self.labels["fen"].image = image

    def activate_button(self, name):
        self.buttons[name]["state"] = "normal"

    def disable_button(self, name):
        self.buttons[name]["state"] = "disabled"


class VideoFrame(tk.Frame):
    def __init__(self, master=None, chess_img_height=340):
        super().__init__(master)
        self.master = master
        self.chess_img_height = chess_img_height

        self.buttons = {}
        self.labels = {}
        self.config_window()

    def create_view(self):
        # Label frame container
        self.container = tk.LabelFrame(master=self, text="Video")
        self.container.rowconfigure(0,  weight=1)
        self.container.columnconfigure(0, weight=1)
        self.container.grid(row=0, column=0, sticky="nsew")

        # video image
        self.labels["frame"] = tk.Label(
            master=self.container)
        self.set_image(Image.new('RGB', (1280, 720)))
        self.labels["frame"].grid(row=0, column=0, sticky="nsew")

        # frames navigation buttons
        self.frm_images_buttons = tk.Frame(master=self.container)
        self.frm_images_buttons.grid(row=1, column=0, sticky="ns")

        # next button
        self.buttons["next_frame"] = tk.Button(
            master=self.frm_images_buttons,
            text="Next(\N{RIGHTWARDS BLACK ARROW})",
            state="disabled")
        self.buttons["next_frame"].grid(row=1, column=2, sticky="e")

        # previous frame button
        self.buttons["previous_frame"] = tk.Button(
            master=self.frm_images_buttons,
            text="Previous(\N{LEFTWARDS BLACK ARROW})",
            state="disabled")
        self.buttons["previous_frame"].grid(row=1, column=0, sticky="w")

        # save frame button
        self.buttons["save_frame"] = tk.Button(
            master=self.frm_images_buttons,
            text="Save(\N{UPWARDS BLACK ARROW})",
            state="disabled")
        self.buttons["save_frame"].grid(row=1, column=1)

    def config_window(self):
        """Configure app's root node (tk.Tk()) i.e. self
        """
        self.rowconfigure(0,  weight=1)
        self.columnconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky="nsew")

    def set_image(self, image):
        """Take a PIL image and resize it
        according to a specified height.
        Display the image in the video frame.

        Args:
            image (PIL.Image)
        """
        image = utils.resize_image(image, self.chess_img_height)
        image = ImageTk.PhotoImage(image)
        self.labels["frame"].configure(image=image)
        self.labels["frame"].image = image

    def activate_button(self, name):
        self.buttons[name]["state"] = "normal"

    def disable_button(self, name):
        self.buttons[name]["state"] = "disabled"


class SideMenuFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master

        self.buttons = {}
        self.string_vars = {}

        self.fps_ratios = [str(i+1) for i in range(10)]

        self.config_window()

    def create_view(self):
        # Label frame container
        self.container = tk.LabelFrame(master=self, text="Menu")
        self.container.rowconfigure(0,  weight=1)
        self.container.columnconfigure(0, weight=1)
        self.container.grid(row=0, column=0, sticky="new")

        # save directory button
        self.buttons["save_dir"] = tk.Button(
            master=self.container, text="Save dir...")
        self.buttons["save_dir"].grid(row=0, column=0, sticky="new")

        # fps ratio option menu
        self.string_vars["fps"] = tk.StringVar(self.container)
        self.string_vars["fps"].set("FPS ratio...")
        self.buttons["fps"] = tk.OptionMenu(self.container,
                                            self.string_vars["fps"],
                                            *self.fps_ratios
                                            )
        self.disable_button("fps")
        self.buttons["fps"].grid(row=1, column=0, sticky="new")

        # load video button
        self.buttons["video"] = tk.Button(
            master=self.container, text="Load video",
            state="disabled")
        self.buttons["video"].grid(row=2, column=0, sticky="new")

        # load pgn button
        self.buttons["pgn"] = tk.Button(
            master=self.container, text="Load PGN",
            state="disabled")
        self.buttons["pgn"].grid(row=3, column=0, sticky="new")

        # reset button
        self.buttons["reset"] = tk.Button(
            master=self.container, text="Reset")
        self.buttons["reset"].grid(row=4, column=0, sticky="sew")

    def config_window(self):
        """Configure app's root node (tk.Tk()) i.e. self
        """
        self.rowconfigure(0,  weight=1)
        self.columnconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky="nsew")

    def activate_button(self, name):
        self.buttons[name]["state"] = "normal"

    def disable_button(self, name):
        self.buttons[name]["state"] = "disabled"
