#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image
import os
import pathlib
import shutil
import pandas as pd

import tkinter as tk
from tkinter import filedialog, simpledialog
from tkinter import messagebox
import traceback

from label_chess import utils, chess2fen
from label_chess.gui.base import Controller
from label_chess.gui import views, controllers, models

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent.parent
PIECES_PATH = os.path.join(ROOT, "resources/pieces")


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


def open_window(root, new_view, new_controller,
                height_ratio, width_factor, top_level=False):
    """Create toplevel window from root window.

    Args:
        root (tk.Tk): tkinter root
        new_view (app.gui.base.View): view class to be opened
            in new window.
        new_controller (app.gui.base.Controller): controller class
            to pair with the view
        height_ratio (float): the new window's height is the
            proportion of the screen height
        width_factor (float): the new window's width is the window's
            height multiplied by this factor.
        top_level (bool, optional): If true, the new window
            is opened in a tk.Toplevel. Defaults to False.
    """
    # create new toplevel window from root Tk object
    window = root
    if top_level:
        window = tk.Toplevel(root)
        window.attributes('-topmost', True)
    # height is a proportion of the screen
    height = int(window.winfo_screenheight() * height_ratio)
    # width is height multiplied by a factor
    width = int(height * width_factor)
    # center new window on screen
    center_window(window, width, height)
    # redirect keyboard to new window
    window.grab_set()
    # create and bind view and controller
    new_view = new_view(master=window, height=height)
    new_controller = new_controller()
    new_controller.bind_view(view=new_view)


class ChessFenAnnotatorController(Controller):
    def __init__(self):
        """Main window of the app. Used
        to open video/pgn file. Navigate
        positions and manage annotations.
        """
        self.view = None
        # path to the chess pieces images
        self.pieces_path = PIECES_PATH
        # when frame is saved popup appears with
        # this color
        self.save_color = "#2CE26E"
        # when frame is unsaved popup appears with
        # this color
        self.unsave_color = "#F4241E"
        # save the original color before the popup
        self.orig_color = ""
        # popup duration in ms
        self.popup_dur = 1000
        # flash duration of a button when activated
        # from the keyboard
        self.flash_dur = 100

        # height of the windows to add video/pgn
        # to the database (proportion of the screen)
        self.add_win_height = 1/7
        # width of the windows to add video/pgn
        # to the database (proportion of the height)
        self.add_win_width = 2

        # init variables to keep track of
        # annotations
        self.setup_variables()

    def bind_view(self, view):
        """Link a view to this controller.
        Bind buttons to method.
        Bind keyboard to buttons.

        Args:
            view (app.gui.base.View)
        """
        self.view = view
        self.view.create_view()

        self.bind_add_video_window()
        self.bind_add_pgn_window()
        self.bind_annotation_management_btns()
        self.setup_keyboard_shortcuts()

    def bind_add_video_window(self):
        """Bind buttons to method for the
        sub-frame managing the game video.
        """
        # get subframe
        video_frame = self.view.frames["video"]
        # load available videos from db to option menu
        video_frame.buttons["select_video"].bind('<Button-1>',
                                                 lambda event: self.populate_menu_buttons(
                                                     query=models.Video.name,
                                                     update_func=video_frame.update_video_list))
        # bind frame navigation buttons to methods
        video_frame.buttons["next_frame"].configure(
            command=self.get_next_frame)
        video_frame.buttons["previous_frame"].configure(
            command=self.get_previous_frame)
        video_frame.buttons["save_frame"].configure(
            command=self.save_frame)
        video_frame.buttons["unsave_frame"].configure(
            command=self.unsave_frame)

        # bind button to function opening new window
        # to add a new video
        video_frame.buttons["add_video"].configure(
            command=lambda: controllers.open_window(
                root=self.view.master,
                new_view=views.VideoLoaderView,
                new_controller=controllers.VideoLoaderController,
                height_ratio=self.add_win_height,
                width_factor=self.add_win_width,
                top_level=True
            )
        )

    def bind_add_pgn_window(self):
        """Bind buttons to method for the
        sub-frame managing the pgn file.
        """
        # get subframe
        pgn_frame = self.view.frames["pgn"]
        # load available pgns from db to option menu
        pgn_frame.buttons["select_pgn"].bind('<Button-1>',
                                             lambda event: self.populate_menu_buttons(
                                                 query=models.PGN.name,
                                                 update_func=pgn_frame.update_pgn_list))
        # bind postion image navigation button to method
        pgn_frame.buttons["skip_fen"].configure(
            command=self.get_next_fen)

        # bind button to function opening new window
        # to add a new pgn fiel
        pgn_frame.buttons["add_pgn"].configure(
            command=lambda: controllers.open_window(
                root=self.view.master,
                new_view=views.PGNLoaderView,
                new_controller=controllers.PGNLoaderController,
                height_ratio=self.add_win_height,
                width_factor=self.add_win_width,
                top_level=True
            )
        )

    def bind_annotation_management_btns(self):
        """Bind buttons to methods for the bottom part
        of the app (create/save/export annoation)
        """
        self.view.buttons["start_button"].configure(
            command=self.start_annotation)

        self.view.buttons["cancel_button"].configure(
            command=self.reset_app)

        self.view.buttons["end_button"].configure(
            command=self.end_annotation)

        self.view.buttons["export_button"].configure(
            command=self.export_annotation)

    def setup_keyboard_shortcuts(self):
        """ Bind keyboard to app's buttons
        """
        video_btns = self.view.frames["video"].buttons
        pgn_btns = self.view.frames["pgn"].buttons

        # bind image navigation buttons to keyboad
        self.view.master.bind('<Left>',
                              lambda event: video_btns["previous_frame"].invoke())  # .flash
        self.view.master.bind('<Right>',
                              lambda event: video_btns["next_frame"].invoke())
        self.view.master.bind('<Up>',
                              lambda event: video_btns["save_frame"].invoke())
        self.view.master.bind('<Down>',
                              lambda event: video_btns["unsave_frame"].invoke())
        self.view.master.bind('<space>',
                              lambda event: pgn_btns["skip_fen"].invoke())

        # bind keyboard events in order to simulate the visual
        # activation of the buttons (flash)
        self.view.master.bind('<Left>', lambda event: self.flash(
            video_btns["previous_frame"], self.flash_dur), add="+")
        self.view.master.bind('<Right>', lambda event: self.flash(
            video_btns["next_frame"], self.flash_dur), add="+")
        self.view.master.bind('<Up>', lambda event: self.flash(
            video_btns["save_frame"], self.flash_dur), add="+")
        self.view.master.bind('<Down>', lambda event: self.flash(
            video_btns["unsave_frame"], self.flash_dur), add="+")
        self.view.master.bind('<space>', lambda event: self.flash(
            pgn_btns["skip_fen"], self.flash_dur), add="+")

    def setup_variables(self):
        """Init/reset the variables used
        to keep track of the current annotation.
        """
        # store the already seen video frames
        # tuples [frame_number, frame img]
        self.frames = []
        # id of the current video frame
        self.current_frame = -1
        # ids of the saved video frames
        self.last_saved_frame = [-1]
        # ids of the saved chess positions
        self.last_saved_fen = [-1]
        # id of the current chess position
        self.current_fen = -1
        # list of tuples (fen string, image of chessboard)
        self.fens = None
        # generator of tuples (video frame, frame original timestep)
        self.frame_generator = None
        # the video and pgn objects used in the current
        # annotation
        self.video, self.pgn = None, None

    def populate_menu_buttons(self, query, update_func):
        """Query the database and call a function
        that takes the result as argument.
        Used to update the content of an option
        menu from the available content in the database.

        Args:
            query (): like models.Video.name
            update_func (func): function that takes
                the query result as input.
        """
        db = models.get_db()
        names = db.query(query).all()
        names = [e[0] for e in names]
        update_func(names)

    def get_object_by_name(self, obj, name):
        """Get an object in the database.
        The object must have a name attribute.
        Name attribute must be unique.

        Args:
            obj (models.*): An ORM class, i.e models.Video
            name (str): name to look for

        Returns:
            type(obj): object found in the database
        """
        db = models.get_db()
        obj = db.query(obj).filter_by(name=name).all()
        return obj[0]

    def start_annotation(self):
        """Load video and pgn to the front end.
        Enable navigation buttons
        """
        # get video and pgn subframes
        video_frame = self.view.frames["video"]
        pgn_frame = self.view.frames["pgn"]

        # get selected video name
        video_name = video_frame.get_selected_video()
        if video_name == "":
            messagebox.showwarning("No video selected",
                                   "Please select a video.")
            return

        # get selected fps ration (only 1/fps_ratio frame is displayed)
        fps_ratio = video_frame.get_selected_fps_ratio()
        if fps_ratio == -1:
            messagebox.showwarning("No fps ratio selected",
                                   "Please select a fps ratio.")
            return
        # get selected pgn name
        pgn_name = pgn_frame.get_selected_pgn()
        if pgn_name == "":
            messagebox.showwarning("No pgn selected",
                                   "Please select a pgn file.")
            return

        # load video and pgn to front end
        self.load_video(video_name, fps_ratio)
        self.load_pgn(pgn_name)

        # activate navigation button and deactivate selection
        # buttons
        self.update_states(caller="start_annotation")

    def load_video(self, video_name, fps_ratio):
        """Load an mp4 video from the database.
        Create a generator of frames for this video.
        Display the first frame in the app.

        Args:
            video_name (str): name of the video to load
                (database attribute)
            fps_ratio (int): only 1 / fps_ratio frame is displayed
                in the app.
        """
        # find video in db
        self.video = self.get_object_by_name(
            models.Video, video_name)
        # generate frames
        self.frame_generator = utils.frames_from_video_generator(
            self.video.path, fps_ratio)
        # display frame
        self.get_next_frame()

        self.view.master.title(f"Chess video FEN annotator - {video_name}")
        self.update_states(caller="load_video")

    def load_pgn(self, pgn_name):
        """Load a pgn file from the database.
        Create a list of png images for the positions
        in the pgn file.
        Display the first png image in the app.

        Args:
            pgn_name (str): name of the pgn file to load
                (database attribute)
        """
        # find pgn in db
        self.pgn = self.get_object_by_name(
            models.PGN, pgn_name)

        # load fens and chessboard representations
        self.fens = chess2fen.get_game_board_images(
            self.pgn.path,
            self.pieces_path
        )
        # display first fen's image
        self.get_next_fen()

        self.update_states(caller="load_pgn")

    def end_annotation(self):
        """Stop current annotation.
        Save results to csv. Add a database
        entry referencing the csv, the video
        and the pgn used for the annotation.
        Reset the annotation states and the
        app's widgets.
        """
        # get the positions of the saved frames/fens
        saved_frames = self.last_saved_frame[1:]
        saved_fens = self.last_saved_fen[1:]

        # create a dataframe with one row per save
        rows = []
        for fen_id, frame_id in zip(saved_fens, saved_frames):
            # get the fen from the list and keep only
            # the string representation
            fen = self.fens[fen_id][0]
            # get the frame from the list of frames
            # and get the original frame id (before fps_ratio)
            frame = self.frames[frame_id][0]
            row = [frame, fen]
            rows.append(row)
        df = pd.DataFrame(rows, columns=["frame_id", "fen"])

        # Get the list of annotations already in the database
        db = models.get_db()
        anns = db.query(models.Annotation).all()
        csv_files = [e.csv_path for e in anns]

        # while the answer is already in the db, open a
        # dialog to ask the user for a name for the annotation
        # file.
        while True:
            csv_name = simpledialog.askstring(
                "Name", "Enter annotation name:", parent=self.view)
            csv_path = os.path.join(models.ANNOTATIONS_DATA_DIR,
                                    f"{csv_name}.csv")
            if csv_path not in csv_files:
                break
        # save csv file and create Annotation object
        # in the database
        try:
            df.to_csv(csv_path, index=False)
            ann = models.Annotation(
                video_url=self.video.url,
                pgn_url=self.pgn.url,
                csv_path=csv_path
            )
            db.add(ann)
            db.commit()
            self.update_states(caller="end_annotation")

        except Exception:
            traceback.print_exc()
            messagebox.showwarning("Annotation",
                                   "Couldn't save annotation.")

        messagebox.showinfo("Annotation",
                            "Successfully saved annotation.")
        self.reset_app()

    def export_annotation(self):
        """Select a subset of the annotations currently
        available in the database and export them in csv
        format to the directory selected by the user.
        """

        # open a dialog to choose a subset of annotations
        # to export
        db = models.get_db()
        anns = db.query(models.Annotation).all()
        options = [
            os.path.split(ann.csv_path)[1] for ann in anns]
        checked_anns = views.export.export_dialog(self.view, options)

        if len(checked_anns) == 0:
            return

        # open a dialog to ask the user for a directory where
        # to export the annotations.
        export_dir = filedialog.askdirectory()
        if not export_dir:
            return

        try:
            # for each selected annotation file
            rows = []
            for ann in checked_anns:
                # path to annotation file in database
                csv_path = os.path.join(
                    models.ANNOTATIONS_DATA_DIR,
                    ann)
                # path to annotation file in export directory
                export_csv_path = os.path.join(
                    export_dir,
                    ann)
                # get annotation object in db and get video url
                # and pgn url
                annotation = db.query(models.Annotation).filter(
                    models.Annotation.csv_path == csv_path).one()
                row = [ann, annotation.video_url,
                       annotation.pgn_url]
                rows.append(row)
                # copy annotation file to export directory
                shutil.copy(csv_path, export_csv_path)

            # save csv file mapping every annotation file
            # to its video/pgn urls
            df = pd.DataFrame(rows, columns=[
                "annotation_file", "video_url", "pgn_url"])
            df_path = os.path.join(
                export_dir, "annotations.csv")
            df.to_csv(df_path, index=True)

        except Exception:
            traceback.print_exc()
            messagebox.showwarning("Export annotation",
                                   "Couldn't export annotation.")
        messagebox.showinfo("Export annotation",
                            "Annotation successfully exported "
                            f"to {export_dir}")

    def get_next_fen(self, event=None):
        """Get the next fen image in the list
        and display it in the gui
        """
        self.current_fen += 1
        next_fen = self.fens[self.current_fen][-1]
        self.view.frames["pgn"].set_image(next_fen)

    def get_next_frame(self, event=None):
        """Get next frame from generator and save it to self.frames
        then replace the current frame with the new frame.
        If self.current_frame is in (-1; len(self.frames)-1) then
        take the frame from the list of already generated frames.
        """
        try:
            self.current_frame += 1

            if self.current_frame > -1 and \
                    self.current_frame < len(self.frames):
                next_frame = self.frames[self.current_frame][-1]
            else:
                next_img, frame_number = next(self.frame_generator)
                next_frame = Image.fromarray(next_img)
                self.frames.append([frame_number, next_frame])
            self.view.frames["video"].set_image(next_frame)

        except StopIteration:
            print(traceback.print_exc())
            self.current_frame -= 1
            self.update_states(caller="next_frame_empty")
            return

        self.update_states(caller="next_frame")

    def get_previous_frame(self, event=None):
        """Go back to positions in self.frames
        and display next frame.
        """
        if self.current_frame > self.last_saved_frame[-1] + 1:
            self.current_frame -= 2
            self.get_next_frame()

        self.update_states(caller="previous_frame")

    def save_frame(self, event=None):
        """Add current fen and frame to the lists
        of saved frames/fen and display next frame/fen
        """
        self.last_saved_frame.append(self.current_frame)
        self.last_saved_fen.append(self.current_fen)

        self.get_next_frame()
        self.get_next_fen()

        self.update_states(caller="save_frame")

    def unsave_frame(self):
        """Revert the last saved frame.
        Remove the last element of the lists
        of save fens and saved frames.
        Set the current fen position to the one
        of the previously saved fen. (since fens
        can be skipped we can't just go back to
        self.current_fen - 1)
        """
        # if at least one frame has been saved
        if len(self.last_saved_frame) > 1:
            # get last saved frame and fen ids
            # and remove them from the save history
            self.last_saved_frame.pop()
            last_save_fen = self.last_saved_fen.pop()
            # plot the last save fen
            self.current_fen = last_save_fen - 1
            self.get_next_fen()

        self.update_states(caller="unsave_frame")

    def label_popup(self, label, color, text, time):
        """Change color and text of a label, then after
        a while, empty text and reset color to original
        color.

        Args:
            label (tk.Label)
            color (str): color to display in label
            text (str): text to display in label
            time (int): waiting time before reset in ms
        """
        # set only once, otherwise if consecutive saves
        # are too fast, the original color ends up being
        # the popup color
        if self.orig_color == "":
            self.orig_color = label.cget("background")

        label.config(
            bg=color, text=text)

        label.after(time, lambda: label.config(bg=self.orig_color, text=""))

    def flash(self, button, time):
        """Change the state of a button to active
        then change it back to original state.

        Args:
            button (tk.button): reference to the button to flash
            time (int): duration in ms before returning the button
                to its original state.
        """
        orig_state = button["state"]
        if orig_state == "normal":
            button.config(state="active")
            button.after(time, lambda: button.config(state=orig_state))

    def reset_app(self, event=None):
        """Stop current annotation, reset annotation states
        and reset widgets.
        """
        self.setup_variables()
        self.bind_view(self.view)

    def update_states(self, caller):
        """Activation/Deactivation of components. To change state
        of components, methods should call this method. This allows
        to centralize the state/transition information in one point.

        Args:
            caller (str): str to identify which method called
                update_states
        """
        if caller == "start_annotation":
            self.view.disable_button("start_button")
            self.view.activate_button("cancel_button")
            self.view.activate_button("end_button")

        elif caller == "end_annotation":
            self.view.activate_button("start_button")
            self.view.disable_button("cancel_button")
            self.view.disable_button("end_button")

        elif caller == "load_video":
            self.view.frames["video"].activate_button("next_frame")
            self.view.frames["video"].disable_button("select_video")
            self.view.frames["video"].disable_button("fps_ratio")

        elif caller == "load_pgn":
            self.view.frames["pgn"].activate_button("skip_fen")
            self.view.frames["video"].activate_button("save_frame")
            self.view.frames["pgn"].disable_button("select_pgn")

        elif caller == "save_frame":
            self.view.frames["video"].disable_button("previous_frame")
            self.view.frames["video"].activate_button("unsave_frame")

            label = self.view.frames["video"].labels["saved"]
            self.label_popup(
                label=label, color=self.save_color, text="frame saved",
                time=self.popup_dur)
        elif caller == "next_frame_empty":
            self.view.frames["video"].disable_button("next_frame")
        elif caller == "next_frame":
            if self.current_frame > 0:
                self.view.frames["video"].activate_button("previous_frame")
        elif caller == "previous_frame":
            self.view.frames["video"].activate_button("next_frame")
            if self.current_frame == self.last_saved_frame[-1] + 1:
                self.view.frames["video"].disable_button("previous_frame")
        elif caller == "unsave_frame":
            # reenable previous frame button
            self.view.frames["video"].activate_button(
                "previous_frame")
            # if no more saved frame in history, disable
            # unsave button
            if len(self.last_saved_frame) < 2:
                self.view.frames["video"].disable_button(
                    "unsave_frame")

            label = self.view.frames["video"].labels["saved"]
            self.label_popup(
                label=label, color=self.unsave_color, text="frame unsaved",
                time=self.popup_dur)
