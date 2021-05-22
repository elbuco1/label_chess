import tkinter as tk
from tkinter import filedialog

from PIL import Image, ImageTk
import os
import pathlib
import json
import shutil

from app import utils, chess2fen
from app.gui.base import Controller
from app.gui import views, controllers, models

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
    new_view = new_view(master=window)
    new_controller = new_controller()
    new_controller.bind_view(view=new_view)


class ChessFenAnnotatorController(Controller):
    def __init__(self):
        self.view = None
        self.pieces_path = PIECES_PATH
        self.setup_variables()
        self.save_color = "#2CE26E"
        self.unsave_color = "#F4241E"
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
        video_frame.buttons["video"].configure(
            command=self.populate_menu_buttons())

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
        # self.populate_menu_buttons()

    def setup_variables(self):
        self.frames = []
        self.current_frame = -1
        self.last_saved_frame = [-1]
        self.last_saved_fen = [-1]
        self.current_fen = -1
        self.fen_images, self.fens = None, None

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

        # resize video image automatically when window is resized
        video_frame = self.view.frames["video"]
        video_frame.bind('<Configure>',
                         lambda event: self.resize_image(video_frame, event))

        # resize pgn image automatically when window is resized
        pgn_frame = self.view.frames["pgn"]
        pgn_frame.bind('<Configure>',
                       lambda event: self.resize_image(pgn_frame, event))

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

    def populate_menu_buttons(self):
        db = models.get_db()
        urls = db.query(models.Video.url).all()
        urls = [e[0] for e in urls]
        self.view.frames["video"].update_video_list(urls)

    def resize_image(self, frame, event):
        """Assuming a view that posess a method
        resize_image that resizes its images based
        on height.

        Args:
            frame (base.View): View with method
                resize_image
        """
        new_height = event.height
        frame.resize_image(new_height)

    def update_states(self, caller):
        """Activation/Deactivation of components. To change state
        of components, methods should call this method. This allows
        to centralize the state/transition information in one point.

        Args:
            caller (str): str to identify which method called
                update_states
        """
        if caller == "select_fps":
            # self.view.frames["side_menu"].activate_button("video")
            pass
        elif caller == "select_save_dir":
            # self.view.frames["side_menu"].activate_button("fps")
            pass
        elif caller == "load_video":
            self.view.frames["video"].activate_button("next_frame")
            # self.view.frames["side_menu"].activate_button("pgn")
            # self.view.frames["side_menu"].disable_button("fps")

        elif caller == "load_pgn":
            self.view.frames["pgn"].activate_button("skip_fen")
            self.view.frames["video"].activate_button("save_frame")
            # self.view.frames["side_menu"].disable_button("video")
        elif caller == "save_frame":
            self.view.frames["video"].disable_button("previous_frame")
            self.view.frames["video"].activate_button("unsave_frame")
            # self.view.frames["side_menu"].disable_button("save_dir")
            # self.view.frames["side_menu"].disable_button("pgn")

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

    # def select_fps(self, *args):
    #     """Select the subsampling rate for the video
    #     before loading the video.
    #     Only once this has been selected can the video
    #     be loaded.
    #     """
    #     side_menu = self.view.frames["side_menu"]
    #     fps_variable = side_menu.string_vars["fps"]
    #     self.fps_ratio = int(fps_variable.get())
    #     self.update_states(caller="select_fps")

    def select_save_dir(self):
        """Open a dialog to select a directory
        where to save frames.
        """
        save_dir = filedialog.askdirectory(
            mustexist=False
        )
        if not save_dir:
            return
        self.save_dir = save_dir
        self.update_states(caller="select_save_dir")

    def load_video(self):
        """Load an mp4 video from file and display the first frame.
        Set a default value for the save directory.
        When loading video, pgn is reset.
        """
        self.video_path = filedialog.askopenfilename(
            filetypes=[("MP4 Files", "*.mp4"), ("All Files", "*.*")]
        )
        if not self.video_path:
            return

        self.frame_generator = utils.frames_from_video_generator(
            self.video_path, self.fps_ratio)

        self.get_next_frame()

        # default save directory
        _, video_name = os.path.split(self.video_path)
        self.view.master.title(f"Chess video FEN annotator - {video_name}")
        self.update_states(caller="load_video")

    def load_pgn(self):
        """Load PGN file and display first fen"""
        self.pgn_path = filedialog.askopenfilename(
            filetypes=[("All Files", "*.*")]
        )
        if not self.pgn_path:
            return

        # load fens and chessboard representations
        self.fen_images, self.fens = chess2fen.get_game_board_images(
            self.pgn_path,
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
        next_fen = self.fen_images[self.current_fen]
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
                next_frame = self.frames[self.current_frame]
            else:
                next_img = next(self.frame_generator)
                next_frame = Image.fromarray(next_img)
                self.frames.append(next_frame)
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

        self.update_states(caller="previous_frame")

    def save_frame(self, event=None):
        """Save currently displayed frame to
        self.save_dir and save matching fen
        to json file with the same name as the frame.
        """
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

        frame = self.frames[self.current_frame]
        fen = self.fens[self.current_fen]

        frame_path, fen_path = self.get_save_paths(
            self.current_frame
        )

        fen = {"fen": fen}
        json.dump(fen, open(fen_path, "w"))

        frame.save(frame_path)
        self.last_saved_frame.append(self.current_frame)
        self.last_saved_fen.append(self.current_fen)

        self.get_next_frame()
        self.get_next_fen()

        self.update_states(caller="save_frame")

    def get_save_paths(self, frame):
        """Get the paths to save frame to jpeg
        and fen to json. Files are named after
        a frame id

        Args:
            frame (int): frame id

        Returns:
            str: jpeg fiel path
            str: json fiel path
        """
        frame_path = os.path.join(
            self.save_dir,
            f"frame{frame}.jpeg"
        )

        fen_path = os.path.join(
            self.save_dir,
            f"frame{frame}.json"
        )
        return frame_path, fen_path

    def unsave_frame(self):
        """Revert the last saved frame
        """
        # if at least one frame has been saved
        if len(self.last_saved_frame) > 1:
            # get last saved frame and fen ids
            # and remove them from the save history
            last_save_frame = self.last_saved_frame.pop()
            last_save_fen = self.last_saved_fen.pop()
            # get paths of last saved frame and fen
            # then delete them
            frame_path, fen_path = self.get_save_paths(
                last_save_frame
            )
            os.remove(frame_path)
            os.remove(fen_path)
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
        orig_color = label.cget("background")
        label.config(
            bg=color, text=text)

        label.after(time, lambda: label.config(bg=orig_color, text=""))

    def flash(self, button, time):
        orig_state = button["state"]
        button.config(state="active")
        button.after(time, lambda: button.config(state=orig_state))

    def reset_app(self, event=None):
        """Reset video and pgn.
        Enable save directory and fps rate selection.
        Disable video and pgn loading
        """
        self.setup_variables()
        self.bind_view(self.view)
