import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os

from chlabel.gui import models
from chlabel.gui.base import Controller


class VideoLoaderController(Controller):
    def __init__(self):
        self.view = None

    def bind_view(self, view):
        self.view = view
        self.view.create_view()
        self.view.buttons["select_video"].configure(command=self.select_video)
        self.view.string_vars["Resolution"].trace("w", self.select_res)
        self.view.buttons["Add"].configure(command=self.add_video_db)

    def select_res(self, *args):
        self.res = self.view.string_vars["Resolution"].get()

    def select_video(self):
        self.video_path = filedialog.askopenfilename(
            filetypes=[("MP4 Files", "*.mp4"), ("All Files", "*.*")]
        )
        if not self.video_path:
            return

    def add_video_db(self):
        if not self.video_path:
            messagebox.showwarning("Please select a video on your computer")
            return

        if not hasattr(self, "res") or \
                self.res not in self.view.resolutions:
            messagebox.showwarning("Invalid resolution",
                                   "Please select a resolution")
            return

        url = self.view.entries["URL"].get()

        if url == "":
            url = self.video_path

        if self.video_exists_in_db(url):
            messagebox.showwarning("Already exists",
                                   f"Video from url: '{url}'"
                                   "already exists in database")
            return

        new_video = models.Video(
            url=url,
            path=self.video_path
        )
        self.persist_video(new_video)

        self.view.entries["URL"].delete(0, 'end')

    def video_exists_in_db(self, url):
        """Check if video url is already
        in database.

        Args:
            url (str)
        """
        db = models.get_db()
        urls = db.query(models.Video.url).all()
        urls = {e[0] for e in urls}
        return url in urls

    def persist_video(self, video):
        """Add video object to db.

        Args:
            video (models.Video): video object
        """
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

    def add_pgn_db(self):
        if not self.pgn_path:
            messagebox.showwarning("Please select a pgn file on your computer")
            return

        url = self.view.entries["URL"].get()

        if url == "":
            url = self.pgn_path

        if self.pgn_exists_in_db(url):
            messagebox.showwarning("Already exists",
                                   f"PGN from url: '{url}'"
                                   "already exists in database")
            return

        new_pgn = models.PGN(
            url=url,
            path=self.pgn_path
        )
        self.persist_pgn(new_pgn)

        self.view.entries["URL"].delete(0, 'end')

    def pgn_exists_in_db(self, url):
        """Check if pgn url is already
        in database.

        Args:
            url (str)
        """
        db = models.get_db()
        urls = db.query(models.PGN.url).all()
        urls = {e[0] for e in urls}
        return url in urls

    def persist_pgn(self, pgn):
        """Add pgn object to db.

        Args:
            pgn (models.PGN): video object
        """
        db = models.get_db()
        db.add(pgn)
        db.commit()
