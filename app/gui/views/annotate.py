import tkinter as tk
from PIL import Image, ImageTk

from app.gui.base import View
from app import utils, chess2fen


class ChessFenAnnotatorView(View):
    def __init__(self, master=None, img_prop=0.85):
        super().__init__(master)
        self.master = master
        self.img_prop = img_prop
        self.config_window()

        self.frames = {}
        self.buttons = {}
        self.menus = {}

    def create_view(self):
        self.frames["annotation"] = AnnotationsFrame(self)
        self.frames["annotation"].create_view()
        self.frames["annotation"].grid(row=0, column=0, sticky="nsew")

        self.container = tk.Frame(master=self)
        self.container.rowconfigure(0,  weight=5)
        self.container.rowconfigure(1,  weight=1)
        self.container.columnconfigure(0, weight=1)
        self.container.grid(row=0, column=1, sticky="nsew")

        # middle
        self.imgs = tk.Frame(master=self.container)
        self.imgs.rowconfigure(0,  weight=1)
        self.imgs.columnconfigure([0, 1], weight=1)
        self.imgs.grid(row=0, column=0, sticky="nsew")

        self.frames["pgn"] = PGNFrame(self.imgs,
                                      img_prop=self.img_prop)
        self.frames["pgn"].create_view()
        self.frames["pgn"].grid(row=0, column=0, sticky="nsew")

        self.frames["video"] = VideoFrame(self.imgs,
                                          img_prop=self.img_prop)
        self.frames["video"].create_view()
        self.frames["video"].grid(row=0, column=1, sticky="nsew")

        # bottom
        self.buttons["start_button"] = tk.Button(self.container, text="START")
        self.buttons["start_button"].grid(row=1, column=0, sticky="nsew")

    def config_window(self):
        """Configure app's root node (tk.Tk()) i.e. self
        """
        self.master.resizable(True, True)
        self.master.rowconfigure(0,  weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.title("Chess video FEN annotator")

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)

        self.rowconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky="nsew")


class AnnotationsFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master

        self.buttons = {}
        self.labels = {}
        self.string_vars = {}

        self.config_window()

    def create_view(self):
        # Label frame container
        self.container = tk.LabelFrame(master=self, text="Annotations")
        self.container.columnconfigure(0,  weight=1)
        self.container.grid(row=0, column=0, sticky="nsew")

        self.buttons["new_ann"] = tk.Button(
            master=self.container, text="New")
        self.buttons["new_ann"].grid(row=0, column=0, sticky="ew")

        self.buttons["load_ann"] = tk.Button(
            master=self.container, text="Load")
        self.buttons["load_ann"].grid(row=1, column=0, sticky="ew")

        self.buttons["save_ann"] = tk.Button(
            master=self.container, text="Save")
        self.buttons["save_ann"].grid(row=2, column=0, sticky="ew")

        self.buttons["export_ann"] = tk.Button(
            master=self.container, text="Export")
        self.buttons["export_ann"].grid(row=3, column=0, sticky="ew")

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

        self.select_frm = tk.Frame(master=self.container)
        self.select_frm.rowconfigure(0,  weight=1)
        self.select_frm.columnconfigure(0,  weight=1)
        self.select_frm.columnconfigure(1,  weight=3)
        self.select_frm.grid(row=0, column=0, sticky="nsew")
        # add pgn
        self.buttons["add_pgn"] = tk.Button(
            master=self.select_frm, text="Add pgn")
        self.buttons["add_pgn"].grid(row=0, column=0, sticky="nsew")
        # select pgn
        self.string_vars["select_pgn"] = tk.StringVar(self.select_frm)
        self.string_vars["select_pgn"].set("Select pgn...")
        self.buttons["select_pgn"] = tk.OptionMenu(master=self.select_frm,
                                                   variable=self.string_vars["select_pgn"],
                                                   value='Select pgn...')
        # self.disable_button("select_pgn")
        self.buttons["select_pgn"].grid(row=0, column=1, sticky="nsew")

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

        # add and select video
        # select video and fps

        self.selection_frm = tk.Frame(master=self.container)
        self.selection_frm.columnconfigure(0, weight=1)
        self.selection_frm.columnconfigure(1, weight=2)
        self.selection_frm.columnconfigure(2, weight=1)
        self.selection_frm.rowconfigure(0,  weight=1)
        self.selection_frm.grid(row=0, column=0, sticky="nsew")

        # add video
        self.buttons["add_video"] = tk.Button(
            master=self.selection_frm, text="Add video")
        self.buttons["add_video"].grid(row=0, column=0, sticky="nsew")

        # select video
        self.string_vars["video"] = tk.StringVar(self.selection_frm)
        self.string_vars["video"].set("Select video...")
        self.buttons["video"] = tk.OptionMenu(master=self.selection_frm,
                                              variable=self.string_vars["video"],
                                              value='Select video...')
        # https://stackoverflow.com/questions/7393430/how-can-i-dynamic-populate-an-option-widget-in-tkinter-depending-on-a-choice-fro/7403530#7403530
        # self.disable_button("video")
        self.buttons["video"].grid(row=0, column=1, sticky="nsew")

        # select fps
        self.string_vars["fps"] = tk.StringVar(self.selection_frm)
        self.string_vars["fps"].set("FPS ratio...")
        self.buttons["fps"] = tk.OptionMenu(master=self.selection_frm,
                                            variable=self.string_vars["fps"],
                                            value='FPS ratio...')
        # self.disable_button("fps")
        self.buttons["fps"].grid(row=0, column=2, sticky="nsew")
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

    def update_video_list(self, options):
        """Change list of video in the menu button

        Args:
            options (list of str): list of video ids
        """
        menu = self.buttons["video"]["menu"]
        menu.delete(0, "end")
        for string in options:
            menu.add_command(label=string,
                             command=lambda value=string:
                             self.string_vars["video"].set(value))

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
