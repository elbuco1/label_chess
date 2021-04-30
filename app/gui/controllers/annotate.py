import tkinter as tk
from tkinter import filedialog

from PIL import Image, ImageTk
import os
import pathlib
import json
import shutil

from app import utils, chess2fen
import Controller

ROOT = pathlib.Path(__file__).resolve().parent.parent
PIECES_PATH = os.path.join(ROOT, "resources/pieces")


class ChessFenAnnotatorController(Controller):
    def __init__(self):
        self.view = None
        self.pieces_path = PIECES_PATH
        self.setup_variables()

    def bind_view(self, view):
        self.view = view
        self.view.create_view()

        # side menu commands
        side_menu = self.view.frames["side_menu"]
        side_menu.string_vars["fps"].trace(
            "w", self.select_fps)
        side_menu.buttons["save_dir"].configure(command=self.select_save_dir)
        side_menu.buttons["video"].configure(command=self.load_video)
        side_menu.buttons["pgn"].configure(command=self.load_pgn)
        side_menu.buttons["reset"].configure(command=self.reset_app)

        # video frame commands
        video_frame = self.view.frames["video"]
        video_frame.buttons["next_frame"].configure(
            command=self.get_next_frame)
        video_frame.buttons["previous_frame"].configure(
            command=self.get_previous_frame)
        video_frame.buttons["save_frame"].configure(
            command=self.save_frame)

        # pgn frame commands
        pgn_frame = self.view.frames["pgn"]
        pgn_frame.buttons["skip_fen"].configure(
            command=self.get_next_fen)

        self.setup_keyboard_shortcuts()

    def setup_variables(self):
        self.frames = []
        self.current_frame = -1
        self.last_saved_frame = -1
        self.video_loaded = False
        self.current_fen = -1
        self.fen_images, self.fens = None, None
        self.pgn_loaded = False

    def setup_keyboard_shortcuts(self):
        """ Associate keys to buttons.
        """
        video_btns = self.view.frames["video"].buttons
        pgn_btns = self.view.frames["pgn"].buttons
        self.view.master.bind('<Left>',
                              lambda event: video_btns["previous_frame"].invoke())  # .flash
        self.view.master.bind('<Right>',
                              lambda event: video_btns["next_frame"].invoke())
        self.view.master.bind('<Up>',
                              lambda event: video_btns["save_frame"].invoke())
        self.view.master.bind('<space>',
                              lambda event: pgn_btns["skip_fen"].invoke())

    def select_fps(self, *args):
        """Select the subsampling rate for the video
        before loading the video.
        Only once this has been selected can the video
        be loaded.
        """
        side_menu = self.view.frames["side_menu"]
        fps_variable = side_menu.string_vars["fps"]
        self.fps_ratio = int(fps_variable.get())
        side_menu.activate_button("video")

    def select_save_dir(self):
        """Open a dialog to select a directory
        where to save frames.
        """
        save_dir = filedialog.askdirectory(
            mustexist=False
        )
        if not save_dir:
            return
        # if os.path.exists(save_dir):
        #     shutil.rmtree(save_dir)
        self.save_dir = save_dir
        self.view.frames["side_menu"].activate_button("fps")

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

        self.view.frames["video"].activate_button("next_frame")
        # self.view.frames["video"].activate_button("save_frame")
        self.view.frames["side_menu"].activate_button("pgn")
        self.view.frames["side_menu"].disable_button("fps")
        self.video_loaded = True

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
        # buttons activation
        self.view.frames["pgn"].activate_button("skip_fen")
        self.view.frames["video"].activate_button("save_frame")
        self.view.frames["side_menu"].disable_button("video")

        # display first fen's image
        self.get_next_fen()

        self.pgn_loaded = True

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
        self.current_frame += 1

        if self.current_frame > -1 and \
                self.current_frame < len(self.frames)-1:
            next_frame = self.frames[self.current_frame]
        else:
            next_img = next(self.frame_generator)
            next_frame = Image.fromarray(next_img)
            self.frames.append(next_frame)

        self.view.frames["video"].set_image(next_frame)

        # enable previous frame button
        previous_frm_btn = self.view.frames["video"].buttons["previous_frame"]
        if previous_frm_btn["state"] == "disabled" and \
                self.current_frame > 0:
            self.view.frames["video"].activate_button("previous_frame")

    def get_previous_frame(self, event=None):
        """Go back to positions in self.frames
        and display next frame.
        """
        if self.current_frame > self.last_saved_frame + 1:
            self.current_frame -= 2
            self.get_next_frame()

        # disable previous frame button
        previous_frm_btn = self.view.frames["video"].buttons["previous_frame"]
        if previous_frm_btn["state"] == "normal" and \
                self.current_frame == self.last_saved_frame + 1:
            self.view.frames["video"].disable_button("previous_frame")

    def save_frame(self, event=None):
        """Save currently displayed frame to
        self.save_dir and save matching fen
        to json file with the same name as the frame.
        """
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

        frame = self.frames[self.current_frame]
        fen = self.fens[self.current_fen]

        frame_path = os.path.join(
            self.save_dir,
            f"frame{self.current_frame}.jpeg"
        )

        fen_path = os.path.join(
            self.save_dir,
            f"frame{self.current_frame}.json"
        )
        fen = {"fen": fen}
        json.dump(fen, open(fen_path, "w"))

        frame.save(frame_path)
        self.last_saved_frame = self.current_frame
        self.get_next_frame()
        self.get_next_fen()

        self.view.frames["video"].disable_button("previous_frame")
        self.view.frames["side_menu"].disable_button("save_dir")
        self.view.frames["side_menu"].disable_button("pgn")

    def reset_app(self, event=None):
        """Reset video and pgn.
        Enable save directory and fps rate selection.
        Disable video and pgn loading
        """
        self.setup_variables()
        self.bind_view(self.view)
