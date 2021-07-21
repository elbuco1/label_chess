#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image, ImageTk, ImageDraw

import tkinter as tk

from label_chess.base import View, ButtonsMixin
from label_chess import utils
from label_chess.views import config as cfg

from fen2pil import draw


class ChessFenAnnotatorView(View, ButtonsMixin):
    def __init__(self, master=None, img_prop=0.8, height=0):
        """App's main window, made of two main subframes.
        One frame is used to display an image representation
        of the chessboard based on a pgn file.

        The other is used to display the frames from a video
        of the live chess game.

        Args:
            master (tk.Tk, optional): tkinter root. Defaults to None.
            img_prop (float, optional): the images height are
                80% of the window's height. Defaults to 0.8.
            height (int, optional): window height. Defaults to 0.
        """
        View.__init__(self, master)
        ButtonsMixin.__init__(self)

        self.master = master
        self.img_prop = img_prop
        self.height = height

        # widgets are grouped per type
        self.frames = {}
        self.menus = {}

        self.config_window()

    def create_view(self):
        """Display frame's widgets
        """
        self.create_imgs_frame()
        self.create_bottom_buttons_frame()

    def create_imgs_frame(self):
        """Frame containing the two subframes
        displaying images (pgn and video)
        """
        self.imgs = tk.Frame(master=self)
        self.imgs.rowconfigure(0,  weight=1)
        self.imgs.columnconfigure([0, 1], weight=1)
        self.imgs.grid(row=0, column=0, sticky="nsew")
        # frame to display pgn file
        self.frames["pgn"] = PGNFrame(self.imgs,
                                      img_prop=self.img_prop,
                                      height=self.height)
        self.frames["pgn"].create_view()
        self.frames["pgn"].grid(row=0, column=0, sticky="nsew")
        # frame to display video frames
        self.frames["video"] = VideoFrame(self.imgs,
                                          img_prop=self.img_prop,
                                          height=self.height)
        self.frames["video"].create_view()
        self.frames["video"].grid(row=0, column=1, sticky="nsew")

    def create_bottom_buttons_frame(self):
        """frame containing the buttons at the bottom
        of the page:

        * start_button: start annotation
        * end_button: stop and save current annotation
        * cancel_button: stop annotation and reset
        * export_button: export annotations from db to file
        """
        self.bottom_btns = tk.Frame(master=self)
        self.bottom_btns.rowconfigure(0,  weight=1)
        self.bottom_btns.columnconfigure([0, 1, 2, 3, 4], weight=1)
        self.bottom_btns.grid(row=1, column=0, sticky="nsew")

        self.buttons["start_button"] = tk.Button(
            self.bottom_btns, text="START", **cfg.BTN())
        self.buttons["start_button"].grid(row=0, column=0, sticky="nsew")

        self.buttons["end_button"] = tk.Button(
            self.bottom_btns, text="END", **cfg.BTN())
        self.buttons["end_button"].grid(row=0, column=1, sticky="nsew")
        self.disable_button("end_button")

        self.buttons["cancel_button"] = tk.Button(
            self.bottom_btns, text="CANCEL", **cfg.BTN())
        self.buttons["cancel_button"].grid(row=0, column=2, sticky="nsew")
        self.disable_button("cancel_button")

        self.buttons["export_button"] = tk.Button(
            self.bottom_btns, text="EXPORT", **cfg.BTN())
        self.buttons["export_button"].grid(row=0, column=3, sticky="nsew")

        self.buttons["reset_button"] = tk.Button(
            self.bottom_btns, text="RESET DB", **cfg.BTN())
        self.buttons["reset_button"].grid(row=0, column=4, sticky="nsew") # disable when annotating

    def config_window(self):
        """Configure Parent window and frame.
        """
        self.master.resizable(False, False)
        self.master.rowconfigure(0,  weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.title("Chess video FEN annotator")

        self.columnconfigure(0, weight=1)
        self.rowconfigure([0, 1], weight=1)
        self.grid(row=0, column=0, sticky="nsew")


class PGNFrame(tk.Frame, ButtonsMixin):
    def __init__(self, master=None, img_prop=0.8, height=0,
                 max_chars_pgn_list=40):
        """Frame to display image representations of PGN file.
        Image is displayed in the central label.

        Args:
            master (tk.Tk/tk.Frame, optional): tkinter parent. Defaults to None.
            img_prop (float, optional): the images height are
                80% of the window's height. Defaults to 0.8.
            height (int, optional): main window's height. Defaults to 0.
            max_chars_pgn_list (int, optional): only the first max_chars_pgn_list
                characters of a pgn file name are displayed in the
                "select_pgn" option menu. Defaults to 40.
        """
        tk.Frame.__init__(self, master)
        ButtonsMixin.__init__(self)

        self.master = master
        self.img_prop = img_prop
        self.height = height
        self.max_chars_pgn_list = max_chars_pgn_list

        self.default_select_option = "Select pgn..."

        self.labels = {}
        self.string_vars = {}

        self.config_window()

    def create_view(self):
        """Frame containing three rows:
        * first row contains one button (add pgn to database) and
            one option menu (select pgn from database)
        * second row contains one label to display a chessboard image
        * third row contains one button (skip to the next image)
        """
        # Main container
        self.container = tk.LabelFrame(master=self, text="Moves", **cfg.LBL_FRM())
        self.container.rowconfigure([0, 2],  weight=1)
        self.container.rowconfigure(1,  weight=2)
        self.container.columnconfigure(0,  weight=1)
        self.container.grid(row=0, column=0, sticky="nsew")

        # first row container
        self.select_frm = tk.Frame(master=self.container)
        self.select_frm.rowconfigure(0,  weight=1)
        self.select_frm.columnconfigure(0,  weight=1)
        self.select_frm.columnconfigure(1,  weight=3)
        self.select_frm.grid(row=0, column=0, sticky="nsew")
        # add pgn
        self.buttons["add_pgn"] = tk.Button(
            master=self.select_frm, text="Add pgn", **cfg.BTN())
        self.buttons["add_pgn"].grid(row=0, column=0, sticky="nsew")
        # select pgn
        self.string_vars["select_pgn"] = tk.StringVar(self.select_frm)
        self.string_vars["select_pgn"].set(self.default_select_option)
        self.buttons["select_pgn"] = tk.OptionMenu(
            master=self.select_frm,
            variable=self.string_vars["select_pgn"],
            value=self.default_select_option)
        self.buttons["select_pgn"].config(**cfg.BTN())
        self.buttons["select_pgn"]["menu"].config(**cfg.BTN())

        self.buttons["select_pgn"].grid(row=0, column=1, sticky="nsew")

        # second row label
        self.labels["fen"] = tk.Label(
            master=self.container)
        self.labels["fen"].grid(row=1, column=0, sticky="nsew")
        self.set_image(draw.create_empty_board())

        # third row next image button
        self.buttons["skip_fen"] = tk.Button(
            master=self.container,
            text="Skip(Space)",
            state="disabled", **cfg.BTN())
        self.buttons["skip_fen"].grid(row=2, column=0, sticky="nsew")

    def config_window(self):
        """Configure frame
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
        """Take a PIL image and save it
        as an attribute of the frame.
        Resize the image to img_prop * height.
        Display the image in the label.

        Args:
            image (PIL.Image)
        """
        self.image = image
        height = int(self.img_prop * self.height)
        image = utils.resize_image(image, height)
        self.display_image(image)

    def update_pgn_list(self, options):
        """Update the list of options in the option
        menu "select_pgn".

        Args:
            options (list of str): list of options
                to display.
        """
        menu = self.buttons["select_pgn"]["menu"]
        menu.delete(0, "end")

        if len(options) == 0:
            options = ["Select pgn..."]

        for option in options:
            menu.add_command(label=option,
                                command=lambda value=option[:self.max_chars_pgn_list]:
                                self.string_vars["select_pgn"].set(value))
            

    def get_selected_pgn(self):
        """Get the value currently selected in the
        "select_pgn" option menu.

        If the selected option is the default option,
        an empty string is returned (this means no option
        is selected).

        Returns:
            str: selected option
        """
        pgn_variable = self.string_vars["select_pgn"]
        pgn_name = pgn_variable.get()

        if pgn_name == self.default_select_option:
            pgn_name = ""
        return pgn_name


class VideoFrame(tk.Frame, ButtonsMixin):
    def __init__(self, master=None, height=0, img_prop=0.8,
                 max_chars_vid_list=80):
        """Frame to display and navigate frames from a chess game
        video.
        Frame is displayed in the central label.

        Args:
            master (tk.Tk/tk.Frame, optional): tkinter parent. Defaults to None.
            height (int, optional): main window's height. Defaults to 0.
            img_prop (float, optional): the images height are
                80% of the window's height. Defaults to 0.8.
            max_chars_pgn_list (int, optional): only the first max_chars_pgn_list
                characters of a pgn file name are displayed in the
                "select_video" option menu. Defaults to 80.
        """

        tk.Frame.__init__(self, master)
        ButtonsMixin.__init__(self)

        self.master = master
        self.img_prop = img_prop
        self.height = height
        self.max_chars_vid_list = max_chars_vid_list

        self.default_video_option = "Select video..."
        self.default_fps_option = "FPS ratio..."

        self.labels = {}
        self.string_vars = {}
        self.config_window()

    def create_view(self):
        """Display frame's widgets
        """
        # Main container
        self.container = tk.LabelFrame(master=self, text="Frames", **cfg.LBL_FRM())
        self.container.rowconfigure([0, 2],  weight=1)
        self.container.rowconfigure(1,  weight=2)

        self.container.columnconfigure(0, weight=1)
        self.container.grid(row=0, column=0, sticky="nsew")

        # video management
        self.create_video_selection(self.container)
        # video image
        self.create_frame_sliders(self.container)
        # navigate frames
        self.create_navigation_buttons(self.container)

    def create_video_selection(self, master):
        """Frame containing buttons to load a video
        to database, select a video from database
        and select a fps ratio
        """
        self.selection_frm = tk.Frame(master=master)
        self.selection_frm.columnconfigure(0, weight=1)
        self.selection_frm.columnconfigure(1, weight=2)
        self.selection_frm.columnconfigure(2, weight=1)
        self.selection_frm.rowconfigure(0,  weight=1)
        self.selection_frm.grid(row=0, column=0, sticky="nsew")

        # add video
        self.buttons["add_video"] = tk.Button(
            master=self.selection_frm, text="Add video", **cfg.BTN())
        self.buttons["add_video"].grid(row=0, column=0, sticky="nsew")

        # select video
        self.string_vars["select_video"] = tk.StringVar(self.selection_frm)
        self.string_vars["select_video"].set(self.default_video_option)
        self.buttons["select_video"] = tk.OptionMenu(
            master=self.selection_frm,
            variable=self.string_vars["select_video"],
            value=self.default_video_option)
        self.buttons["select_video"].config(**cfg.BTN())
        self.buttons["select_video"]["menu"].config(**cfg.BTN())
        self.buttons["select_video"].grid(row=0, column=1, sticky="nsew")

        # select fps
        fps_options = [1, 5, 10, 15, 20, 25, 30]

        self.string_vars["fps_ratio"] = tk.StringVar(self.selection_frm)
        self.string_vars["fps_ratio"].set(self.default_fps_option)
        self.buttons["fps_ratio"] = tk.OptionMenu(self.selection_frm,
                                                  self.string_vars["fps_ratio"],
                                                  *fps_options)
        self.buttons["fps_ratio"].config(**cfg.BTN())
        self.buttons["fps_ratio"]["menu"].config(**cfg.BTN())
        self.buttons["fps_ratio"].grid(row=0, column=2, sticky="nsew")

    def create_frame_sliders(self, master):
        """Frame containing img from chess game video and
        sliders to select a part of the img.
        """
        # container for img + sliders
        self.frm_img = tk.Frame(master=master)
        self.frm_img.rowconfigure([0, 1, 2], weight=1)
        self.frm_img.columnconfigure(0, weight=1)
        self.frm_img.grid(row=1, column=0, sticky="nsew")

        # sub container for image and right side vertical sliders
        self.frm_img_right_slider = tk.Frame(master=self.frm_img)
        self.frm_img_right_slider.columnconfigure([0, 1, 2], weight=1)
        self.frm_img_right_slider.rowconfigure(0, weight=1)

        self.frm_img_right_slider.grid(row=1, column=0, sticky="nsew")

        # img
        self.labels["frame"] = tk.Label(
            master=self.frm_img_right_slider)
        self.labels["frame"].grid(row=0, column=1, sticky="nsew")
        self.set_image(Image.new('RGB', (1280, 720)))

        # side sliders
        self.buttons["slider_left"] = tk.Scale(
            master=self.frm_img_right_slider,
            from_=0,
            to=100,
            width=10,
            showvalue=False,
            sliderlength=10
        )
        self.buttons["slider_left"].set(0)
        self.buttons["slider_left"].grid(row=0, column=0, sticky="nsew")
        self.disable_button("slider_left")

        self.buttons["slider_right"] = tk.Scale(
            master=self.frm_img_right_slider,
            from_=0,
            to=100,
            width=10,
            showvalue=False,
            sliderlength=10
        )
        self.buttons["slider_right"].set(100)
        self.buttons["slider_right"].grid(row=0, column=2, sticky="nsew")
        self.disable_button("slider_right")

        # align top and bottom sliders to image width
        aspect_ratio = 9/16
        img_width_prop = 35/1000
        padding = int(self.height * aspect_ratio * img_width_prop)

        # bottom sliders
        self.buttons["slider_top"] = tk.Scale(
            master=self.frm_img,
            from_=0,
            to=100,
            width=10,
            orient=tk.HORIZONTAL,
            showvalue=False,
            sliderlength=10
        )
        self.buttons["slider_top"].set(0)
        self.buttons["slider_top"].grid(
            row=0, column=0, sticky="nsew", padx=padding)

        self.disable_button("slider_top")

        self.buttons["slider_bottom"] = tk.Scale(
            master=self.frm_img,
            from_=0,
            to=100,
            width=10,
            orient=tk.HORIZONTAL,
            showvalue=False,
            sliderlength=10
        )
        self.buttons["slider_bottom"].set(100)
        self.buttons["slider_bottom"].grid(
            row=2, column=0, sticky="nsew", padx=padding)
        self.disable_button("slider_bottom")

    def create_navigation_buttons(self, master):
        """Frame containing buttons to navigate
        video frames (previous, next) and save/unsave
        a frame.
        """
        # frames navigation buttons
        self.frm_images_buttons = tk.Frame(master=master)
        self.frm_images_buttons.grid(row=2, column=0, sticky="nsew")
        self.frm_images_buttons.rowconfigure(0,  weight=1)
        self.frm_images_buttons.columnconfigure([0, 1, 2, 3, 4], weight=1)

        # previous frame button
        self.buttons["previous_frame"] = tk.Button(
            master=self.frm_images_buttons,
            text="Previous(Left)",
            state="disabled", **cfg.BTN())
        self.buttons["previous_frame"].grid(row=0, column=0, sticky="nsew")

        # save frame button
        self.buttons["save_frame"] = tk.Button(
            master=self.frm_images_buttons,
            text="Save(Up)",
            state="disabled", **cfg.BTN())
        self.buttons["save_frame"].grid(row=0, column=1, sticky="nsew")

        # unsave frame button
        self.buttons["unsave_frame"] = tk.Button(
            master=self.frm_images_buttons,
            text="Unsave(Down)",
            state="disabled", **cfg.BTN())
        self.buttons["unsave_frame"].grid(row=0, column=3, sticky="nsew")

        # next button
        self.buttons["next_frame"] = tk.Button(
            master=self.frm_images_buttons,
            text="Next(Right)",
            state="disabled", **cfg.BTN())
        self.buttons["next_frame"].grid(row=0, column=4, sticky="nsew")

        # label to display popup when frame is saves
        self.labels["saved"] = tk.Label(
            master=self.frm_images_buttons)
        self.labels["saved"].grid(row=0, column=2, sticky="nsew")

    def config_window(self):
        """Configure frame
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

    def set_image(self, image,
                  top_left=None,
                  bottom_right=None):
        """Take a PIL image and save it
        as an attribute of the frame.
        Resize the image to img_prop * height.
        Display the image in the label.

        Draw rectangle on image.


        Args:
            image (PIL.Image)
            top_left (tuple, optional): if specified, top left
                corner of rectangle to draw on image. Position
                is expressed as percentage of the image width
                and height respectively. Defaults to None.
            bottom_right (tuple, optional): if specified, bottom right.
                corner of rectangle to draw on image. Position
                is expressed as percentage of the image width
                and height respectively. Defaults to None.
        """
        self.image = image
        height = int(self.img_prop * self.height)
        image = utils.resize_image(image, height)

        if top_left is not None and bottom_right is not None:
            draw = ImageDraw.Draw(image)
            width, height = image.size

            top_left = tuple([
                int(top_left[0] * width / 100),
                int(top_left[1] * height / 100)
            ])

            bottom_right = tuple([
                int(bottom_right[0] * width / 100) - 1,
                int(bottom_right[1] * height / 100)-1
            ])

            draw.rectangle([top_left, bottom_right],
                           outline="red", width=3)
        self.display_image(image)

    def update_video_list(self, options):
        """Update the list of options in the option
        menu "select_video".

        Args:
            options (list of str): list of options
                to display.
        """
        menu = self.buttons["select_video"]["menu"]
        menu.delete(0, "end")

        if len(options) == 0:
            options = ["Select video..."]

        for option in options:
            menu.add_command(label=option,
                                command=lambda value=option:
                                self.string_vars["select_video"].set(value))

    def get_selected_video(self):
        """Get the value currently selected in the
        "select_video" option menu.

        If the selected option is the default option,
        an empty string is returned (this means no option
        is selected).

        Returns:
            str: selected option
        """
        video_variable = self.string_vars["select_video"]
        video_name = video_variable.get()

        if video_name == self.default_video_option:
            video_name = ""
        return video_name

    def get_selected_fps_ratio(self):
        """Get the value currently selected in the
        "fps_ratio" option menu.

        If the selected option is the default option,
        an empty string is returned (this means no option
        is selected).

        Returns:
            str: selected option
        """
        fps_variable = self.string_vars["fps_ratio"]
        fps = fps_variable.get()

        if fps == self.default_fps_option:
            fps = -1
        return int(fps)
