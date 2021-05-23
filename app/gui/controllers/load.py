import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
import shutil

from app.gui import models
from app.gui.base import Controller


class VideoLoaderController(Controller):
    def __init__(self):
        self.view = None

    def bind_view(self, view):
        self.view = view
        self.view.create_view()
        self.view.buttons["select_video"].configure(command=self.select_video)
        self.view.buttons["Add"].configure(command=self.add_video_db)

    def select_video(self):
        self.video_path = filedialog.askopenfilename(
            filetypes=[("MP4 Files", "*.mp4"), ("All Files", "*.*")]
        )
        if not self.video_path:
            return
        label = self.view.labels["select_video"]
        label.configure(
            text=os.path.split(self.video_path)[-1])

    def add_video_db(self):
        if not self.video_path:
            messagebox.showwarning("Please select a video on your computer")
            return

        url = self.view.entries["URL"].get()

        if url == "":
            url = self.video_path

        video_name = os.path.split(self.video_path)[-1]
        video_name = video_name.replace(" ", "_").lower()

        if self.video_exists_in_db(url, video_name):
            messagebox.showwarning("Already exists",
                                   f"Video "
                                   "already exists in database")
            return

        db_path = os.path.join(models.VIDEO_DATA_DIR,
                               video_name)

        new_video = models.Video(
            url=url,
            original_path=self.video_path,
            path=db_path,
            name=video_name)

        self.persist_video(new_video,
                           original_path=self.video_path,
                           db_path=db_path)

        messagebox.showinfo("Video",
                            "Video successfully added to database.")

        self.view.entries["URL"].delete(0, 'end')
        label = self.view.labels["select_video"]
        label.configure(text="")

    def video_exists_in_db(self, url, name):
        """Check if video url or name is already
        in database.

        Args:
            url (str)
            name (str)
        """
        db = models.get_db()
        urls = db.query(models.Video.url).all()
        names = db.query(models.Video.name).all()

        urls = {e[0] for e in urls}
        names = {e[0] for e in names}

        return url in urls or name in names

    def persist_video(self, video, original_path, db_path):
        """Add video object to db.
        Copy video to app storage.

        Args:
            video (models.Video): video object
        """
        shutil.copy(original_path, db_path)
        db = models.get_db()
        db.add(video)
        db.commit()


class PGNLoaderController(Controller):
    def __init__(self):
        self.view = None

    def bind_view(self, view):
        self.view = view
        self.view.create_view()
        self.view.buttons["select_pgn"].configure(command=self.select_pgn)
        self.view.buttons["Add"].configure(command=self.add_pgn_db)

    def select_pgn(self):
        self.pgn_path = filedialog.askopenfilename(
            filetypes=[("All Files", "*.*")]
        )
        if not self.pgn_path:
            return

        label = self.view.labels["select_pgn"]
        label.configure(
            text=os.path.split(self.pgn_path)[-1])

    def add_pgn_db(self):
        if not self.pgn_path:
            messagebox.showwarning("Please select a pgn file on your computer")
            return

        url = self.view.entries["URL"].get()

        if url == "":
            url = self.pgn_path

        pgn_name = os.path.split(self.pgn_path)[-1]
        pgn_name = pgn_name.replace(" ", "_").lower()

        if self.pgn_exists_in_db(url, pgn_name):
            messagebox.showwarning("Already exists",
                                   f"PGN "
                                   "already exists in database")
            return

        db_path = os.path.join(models.PGN_DATA_DIR,
                               pgn_name)

        new_pgn = models.PGN(
            url=url,
            original_path=self.pgn_path,
            path=db_path,
            name=pgn_name
        )
        self.persist_pgn(new_pgn,
                         original_path=self.pgn_path,
                         db_path=db_path)

        messagebox.showinfo("PGN",
                            "PGN successfully added to database.")

        self.view.entries["URL"].delete(0, 'end')
        label = self.view.labels["select_pgn"]
        label.configure(text="")

    def pgn_exists_in_db(self, url, name):
        """Check if pgn url is already
        in database.

        Args:
            url (str)
            name (str)
        """
        db = models.get_db()
        urls = db.query(models.PGN.url).all()
        names = db.query(models.PGN.name).all()

        urls = {e[0] for e in urls}
        names = {e[0] for e in names}
        return url in urls or name in names

    def persist_pgn(self, pgn, original_path, db_path):
        """Add pgn object to db.
        Copy pgn to app storage.
        Args:
            pgn (models.PGN): video object
        """
        shutil.copy(original_path, db_path)

        db = models.get_db()
        db.add(pgn)
        db.commit()
