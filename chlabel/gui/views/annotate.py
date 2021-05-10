import tkinter as tk
from PIL import Image, ImageTk

from .base import View
from chlabel import utils, chess2fen


class ChessFenAnnotatorView(View):
    def __init__(self, master=None, img_prop=0.8):
        super().__init__(master)
        self.master = master
        self.img_prop = img_prop
        self.config_window()

        self.frames = {}
        self.buttons = {}

    def create_view(self):
        self.container = tk.Frame(master=self)
        self.container.rowconfigure(0,  weight=1)
        self.container.columnconfigure(0, weight=1)
        self.container.columnconfigure(1, weight=1)
        self.container.grid(row=0, column=0, sticky="nsew")

        self.frames["pgn"] = PGNFrame(self.container,
                                      img_prop=self.img_prop)
        self.frames["pgn"].create_view()
        self.frames["pgn"].grid(row=0, column=0, sticky="nsew")

        self.frames["video"] = VideoFrame(self.container,
                                          img_prop=self.img_prop)
        self.frames["video"].create_view()
        self.frames["video"].grid(row=0, column=1, sticky="nsew")

        self.buttons["start_button"] = tk.Button(self, text="START")
        self.buttons["start_button"].grid(row=1, column=0, sticky="nsew")

    def config_window(self):
        """Configure app's root node (tk.Tk()) i.e. self
        """
        self.master.resizable(True, True)
        self.master.rowconfigure(0,  weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.title("Chess video FEN annotator")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=5)
        self.rowconfigure(1, weight=1)
        self.grid(row=0, column=0, sticky="nsew")


class PGNFrame(tk.Frame):
    def __init__(self, master=None, img_prop=0.9):
        super().__init__(master)
        self.master = master
        self.img_prop = img_prop

        self.buttons = {}
        self.labels = {}
        self.string_vars = {}

        self.config_window()

    def create_view(self):
        # Label frame container
        self.container = tk.LabelFrame(master=self, text="Moves")
        self.container.rowconfigure([0, 2],  weight=1)
        self.container.rowconfigure(1,  weight=2)
        self.container.columnconfigure(0,  weight=1)
        self.container.grid(row=0, column=0, sticky="nsew")

        # select pgn
        self.string_vars["pgn"] = tk.StringVar(self.container)
        self.string_vars["pgn"].set("Select pgn...")
        self.buttons["pgn"] = tk.OptionMenu(master=self.container,
                                            variable=self.string_vars["pgn"],
                                            value='Select pgn...')
        self.disable_button("pgn")
        self.buttons["pgn"].grid(row=0, column=0, sticky="nsew")

        # chess fen
        self.labels["fen"] = tk.Label(
            master=self.container)
        self.labels["fen"].grid(row=1, column=0, sticky="nsew")
        self.set_image(chess2fen.create_empty_board())

        # skip fen button
        self.buttons["skip_fen"] = tk.Button(
            master=self.container,
            text="Skip(Space)",
            state="disabled")
        self.buttons["skip_fen"].grid(row=2, column=0, sticky="nsew")

    def config_window(self):
        """Configure app's root node (tk.Tk()) i.e. self
        """
        self.rowconfigure(0,  weight=1)
        self.columnconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky="nsew")

    def display_image(self, image):
        """Plot image in label
        Args:
            image (PiL.Image)
        """
        image = ImageTk.PhotoImage(image)
        self.labels["fen"].configure(image=image)
        self.labels["fen"].image = image

    def set_image(self, image):
        """Take a PIL image save it as an attribute
        of the view and display it in a label.
        Args:
            image (PIL.Image)
        """
        self.image = image
        self.display_image(image)

    def resize_image(self, height):
        """Resize pgn image based on new height.
        Provides the controller with a method that
        resizes the image.

        Args:
            height (int): new height for image
        """
        image_height = int(self.img_prop*height)
        image = utils.resize_image(self.image, image_height)
        self.display_image(image)

    def activate_button(self, name):
        self.buttons[name]["state"] = "normal"

    def disable_button(self, name):
        self.buttons[name]["state"] = "disabled"


class VideoFrame(tk.Frame):
    def __init__(self, master=None, img_prop=0.9):
        super().__init__(master)
        self.master = master
        self.img_prop = img_prop

        self.buttons = {}
        self.labels = {}
        self.string_vars = {}
        self.config_window()

    def create_view(self):
        # Label frame container
        self.container = tk.LabelFrame(master=self, text="Frames")
        self.container.rowconfigure([0, 2],  weight=1)
        self.container.rowconfigure(1,  weight=2)

        self.container.columnconfigure(0, weight=1)
        self.container.grid(row=0, column=0, sticky="nsew")

        # select video and fps
        self.selection_frm = tk.Frame(master=self.container)
        self.selection_frm.columnconfigure(0, weight=5)
        self.selection_frm.columnconfigure(1, weight=1)
        self.selection_frm.rowconfigure(0,  weight=1)
        self.selection_frm.grid(row=0, column=0, sticky="nsew")

        # select video
        self.string_vars["video"] = tk.StringVar(self.selection_frm)
        self.string_vars["video"].set("Select video...")
        self.buttons["video"] = tk.OptionMenu(master=self.selection_frm,
                                              variable=self.string_vars["video"],
                                              value='Select video...')
        self.disable_button("video")
        self.buttons["video"].grid(row=0, column=0, sticky="nsew")

        # select fps
        self.string_vars["fps"] = tk.StringVar(self.selection_frm)
        self.string_vars["fps"].set("FPS ratio...")
        self.buttons["fps"] = tk.OptionMenu(master=self.selection_frm,
                                            variable=self.string_vars["fps"],
                                            value='FPS ratio...')
        self.disable_button("fps")
        self.buttons["fps"].grid(row=0, column=1, sticky="nsew")
        # video image
        self.labels["frame"] = tk.Label(
            master=self.container)
        self.labels["frame"].grid(row=1, column=0, sticky="nsew")
        self.set_image(Image.new('RGB', (1280, 720)))

        # frames navigation buttons
        self.frm_images_buttons = tk.Frame(master=self.container)
        self.frm_images_buttons.grid(row=2, column=0, sticky="nsew")
        self.frm_images_buttons.rowconfigure(0,  weight=1)
        self.frm_images_buttons.columnconfigure([0, 1, 2, 3, 4], weight=1)

        # previous frame button
        self.buttons["previous_frame"] = tk.Button(
            master=self.frm_images_buttons,
            text="Previous(\N{LEFTWARDS BLACK ARROW})",
            state="disabled")
        self.buttons["previous_frame"].grid(row=0, column=0, sticky="nsew")

        # save frame button
        self.buttons["save_frame"] = tk.Button(
            master=self.frm_images_buttons,
            text="Save(\N{UPWARDS BLACK ARROW})",
            state="disabled")
        self.buttons["save_frame"].grid(row=0, column=1, sticky="nsew")

        # unsave frame button
        self.buttons["unsave_frame"] = tk.Button(
            master=self.frm_images_buttons,
            text="Unsave(\N{DOWNWARDS BLACK ARROW})",
            state="disabled")
        self.buttons["unsave_frame"].grid(row=0, column=3, sticky="nsew")

        # next button
        self.buttons["next_frame"] = tk.Button(
            master=self.frm_images_buttons,
            text="Next(\N{RIGHTWARDS BLACK ARROW})",
            state="disabled")
        self.buttons["next_frame"].grid(row=0, column=4, sticky="nsew")

        # label to display popup when frame is saves
        self.labels["saved"] = tk.Label(
            master=self.frm_images_buttons)
        self.labels["saved"].grid(row=0, column=2, sticky="nsew")

    def config_window(self):
        """Configure app's root node (tk.Tk()) i.e. self
        """
        self.rowconfigure(0,  weight=1)
        self.columnconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky="nsew")

    def display_image(self, image):
        """Plot image in label
        Args:
            image (PiL.Image)
        """
        image = ImageTk.PhotoImage(image)
        self.labels["frame"].configure(image=image)
        self.labels["frame"].image = image

    def set_image(self, image):
        """Take a PIL image and save it
        as an attribute of the view.
        Display the image in the video label.

        Args:
            image (PIL.Image)
        """
        self.image = image
        self.display_image(image)

    def resize_image(self, height):
        """Resize video image based on new height.
        Provides the controller with a method that
        resizes the image.

        Args:
            height (int): new height for image
        """
        image_height = int(self.img_prop*height)
        image = utils.resize_image(self.image, image_height)
        self.display_image(image)

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
        self.container.columnconfigure(0, weight=1)
        self.container.grid(row=0, column=0, sticky="nsew")

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
