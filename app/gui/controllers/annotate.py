import tkinter as tk
from tkinter import filedialog, simpledialog
from tkinter import messagebox
import traceback

from PIL import Image, ImageTk
import os
import pathlib
import json
import shutil
import time
from app import utils, chess2fen
from app.gui.base import Controller
from app.gui import views, controllers, models
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
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
    """ Open a window from top window
    """
    # create new window from root Tk object
    window = root
    if top_level:
        window = tk.Toplevel(root)
        window.attributes('-topmost', True)
        # root.iconify()

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
        self.view = None
        self.pieces_path = PIECES_PATH
        self.setup_variables()
        self.save_color = "#2CE26E"
        self.unsave_color = "#F4241E"
        self.orig_color = ""
        self.popup_dur = 1000
        self.flash_dur = 100

        self.video_height = 1/7
        self.video_width = 2

        self.pgn_height = 1/7
        self.pgn_width = 2

    def bind_view(self, view):
        self.view = view
        self.view.create_view()

        # video frame commands
        video_frame = self.view.frames["video"]

        video_frame.buttons["select_video"].bind('<Button-1>',
                                                 lambda event: self.populate_menu_buttons(
                                                     query=models.Video.name,
                                                     update_func=video_frame.update_video_list))
        video_frame.buttons["next_frame"].configure(
            command=self.get_next_frame)
        video_frame.buttons["previous_frame"].configure(
            command=self.get_previous_frame)
        video_frame.buttons["save_frame"].configure(
            command=self.save_frame)
        video_frame.buttons["unsave_frame"].configure(
            command=self.unsave_frame)
        # open download video window
        video_frame.buttons["add_video"].configure(
            command=lambda: controllers.open_window(
                root=self.view.master,
                new_view=views.VideoLoaderView,
                new_controller=controllers.VideoLoaderController,
                height_ratio=self.video_height,
                width_factor=self.video_width,
                top_level=True
            )
        )

        # pgn frame commands
        pgn_frame = self.view.frames["pgn"]

        pgn_frame.buttons["select_pgn"].bind('<Button-1>',
                                             lambda event: self.populate_menu_buttons(
                                                 query=models.PGN.name,
                                                 update_func=pgn_frame.update_pgn_list))
        pgn_frame.buttons["skip_fen"].configure(
            command=self.get_next_fen)
        # open download pgn window
        pgn_frame.buttons["add_pgn"].configure(
            command=lambda: controllers.open_window(
                root=self.view.master,
                new_view=views.PGNLoaderView,
                new_controller=controllers.PGNLoaderController,
                height_ratio=self.pgn_height,
                width_factor=self.pgn_width,
                top_level=True
            )
        )

        self.setup_keyboard_shortcuts()

        # footer binds
        self.view.buttons["start_button"].configure(
            command=self.start_annotation)

        self.view.buttons["cancel_button"].configure(
            command=self.reset_app)

        self.view.buttons["end_button"].configure(
            command=self.end_annotation)

        self.view.buttons["export_button"].configure(
            command=self.export_annotation)

    def setup_variables(self):
        self.frames = []
        self.current_frame = -1
        self.last_saved_frame = [-1]
        self.last_saved_fen = [-1]
        self.current_fen = -1
        self.fens, self.frame_generator = None, None
        self.video, self.pgn = None, None

    def setup_keyboard_shortcuts(self):
        """ Associate keys to buttons.
        """
        video_btns = self.view.frames["video"].buttons
        pgn_btns = self.view.frames["pgn"].buttons
        # bind commands to buttons
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
        # flash buttons
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

    def populate_menu_buttons(self, query, update_func):
        db = models.get_db()
        names = db.query(query).all()
        names = [e[0] for e in names]
        update_func(names)

    def get_object_by_name(self, obj, name):
        db = models.get_db()
        obj = db.query(obj).filter_by(name=name).all()
        return obj[0]

    def start_annotation(self):
        # get selected video name
        video_frame = self.view.frames["video"]
        pgn_frame = self.view.frames["pgn"]

        video_name = video_frame.get_selected_video()
        if video_name == "":
            messagebox.showwarning("No video selected",
                                   "Please select a video.")
            return

        fps_ratio = video_frame.get_selected_fps_ratio()
        if fps_ratio == -1:
            messagebox.showwarning("No fps ratio selected",
                                   "Please select a fps ratio.")
            return
        pgn_name = pgn_frame.get_selected_pgn()
        if pgn_name == "":
            messagebox.showwarning("No pgn selected",
                                   "Please select a pgn file.")
            return

        self.load_video(video_name, fps_ratio)
        self.load_pgn(pgn_name)

        self.update_states(caller="start_annotation")

    def export_annotation(self):
        db = models.get_db()
        anns = db.query(models.Annotation).all()
        options = [
            os.path.split(ann.csv_path)[1] for ann in anns]
        checks = views.export.export_dialog(self.view, options)

    def end_annotation(self):
        saved_frames = self.last_saved_frame[1:]
        saved_fens = self.last_saved_fen[1:]
        rows = []
        for fen_id, frame_id in zip(saved_fens, saved_frames):
            fen = self.fens[fen_id][0]
            frame = self.frames[frame_id][0]
            row = [frame, fen]
            rows.append(row)
        df = pd.DataFrame(rows, columns=["frame_id", "fen"])

        # ask for annotation name(must be unique)
        db = models.get_db()

        anns = db.query(models.Annotation).all()
        csv_files = [e.csv_path for e in anns]

        while True:
            csv_name = simpledialog.askstring(
                "Name", "Enter annotation name:", parent=self.view)
            csv_path = os.path.join(models.ANNOTATIONS_DATA_DIR,
                                    f"{csv_name}.csv")
            if csv_path not in csv_files:
                break

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

    def load_video(self, video_name, fps_ratio):
        """Load an mp4 video from file and display the first frame.
        Set a default value for the save directory.
        When loading video, pgn is reset.
        """
        self.video = self.get_object_by_name(
            models.Video, video_name)

        self.frame_generator = utils.frames_from_video_generator(
            self.video.path, fps_ratio)

        self.get_next_frame()
        # default save directory
        self.view.master.title(f"Chess video FEN annotator - {video_name}")
        self.update_states(caller="load_video")

    def load_pgn(self, pgn_name):
        """Load PGN file and display first fen"""
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
                    self.current_frame < len(self.frames)-1:
                next_frame = self.frames[self.current_frame][-1]
            else:
                next_img, frame_number = next(self.frame_generator)
                next_frame = Image.fromarray(next_img)
                self.frames.append([frame_number, next_frame])
            self.view.frames["video"].set_image(next_frame)

        except StopIteration:
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

        self.update_states(caller="previous_frame")  # TODO decorator?

    def save_frame(self, event=None):
        """
        """
        self.last_saved_frame.append(self.current_frame)
        self.last_saved_fen.append(self.current_fen)

        self.get_next_frame()
        self.get_next_fen()

        self.update_states(caller="save_frame")

    def unsave_frame(self):
        """Revert the last saved frame
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
        if self.orig_color == "":
            self.orig_color = label.cget("background")

        label.config(
            bg=color, text=text)

        label.after(time, lambda: label.config(bg=self.orig_color, text=""))

    def flash(self, button, time):
        orig_state = button["state"]
        if orig_state == "normal":
            button.config(state="active")
            button.after(time, lambda: button.config(state=orig_state))

    def reset_app(self, event=None):
        """Reset video and pgn.
        Enable save directory and fps rate selection.
        Disable video and pgn loading
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
