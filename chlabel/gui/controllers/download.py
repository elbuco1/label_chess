import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os

from chlabel import utils
from chlabel.gui import models
from .base import Controller


class VideoDownloaderController(Controller):
    def __init__(self):
        self.view = None

    def bind_view(self, view):
        self.view = view
        self.view.create_view()
        self.view.buttons["Download"].configure(command=self.download_video)
        self.view.string_vars["Resolution"].trace("w", self.select_res)

    def select_res(self, *args):
        self.res = self.view.string_vars["Resolution"].get()

    def download_video(self):
        """Download a youtube video, using information
        collected from the view.
        """
        if not hasattr(self, "res") or \
                self.res not in self.view.resolutions:
            messagebox.showwarning("Invalid resolution",
                                   "Please select a resolution")
            return

        url = self.view.entries["URL"].get()

        if self.video_exists(url):
            messagebox.showwarning("Already exists",
                                   f"Video from url: '{url}'"
                                   "already exists in database")
            return

        if len(url) > 0:
            file_path = self.select_save_dir()
            if file_path is not None:
                file_name, ext = file_path.split(".")
                save_dir, file_name = os.path.split(file_name)

                messagebox.showinfo("Download started",
                                    f"Video at url: '{url}' with resolution '{self.res}' "
                                    "is being downloaded "
                                    f"to '{file_path}'."
                                    )
                try:
                    utils.download_video(
                        url=url,
                        save_path=save_dir,
                        file_name=file_name,
                        file_extension=ext,
                        res=self.res
                    )
                    # TODO return res, if different info box
                except Exception:
                    messagebox.showerror("Download failed",
                                         f"Video at url: '{url}' with resolution '{self.res}' "
                                         "could not be downloaded "
                                         f"to '{file_path}'."
                                         )
                    return
                # insert new video object in database
                new_video = models.Video(
                    url=url,
                    path=file_path
                )
                self.persist_video(new_video)

                messagebox.showinfo("Download completed",
                                    f"Video at url: '{url}' with resolution '{self.res}' "
                                    "has been downloaded "
                                    f"to '{file_path}'."
                                    )
                self.view.entries["URL"].delete(0, 'end')
        else:
            messagebox.showwarning("Invalid url",
                                   "Please enter a url")
            return

    def video_exists(self, url):
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

    def select_save_dir(self):
        files = [
            ('Video Files', '*.mp4')
        ]
        file_path = filedialog.asksaveasfile(
            filetypes=files,
            defaultextension=files)
        if not file_path:
            return None
        return file_path.name


class FileDownloaderController(Controller):
    def __init__(self):
        self.view = None

    def bind_view(self, view):
        self.view = view
        self.view.create_view()
        self.view.buttons["Download"].configure(command=self.download_file)

    def download_file(self):
        """Download a file from the internet
        """
        url = self.view.entries["URL"].get()
        if len(url) > 0:
            file_path = self.select_save_dir()
            if file_path is not None:
                print(file_path)
                save_dir, file_name = os.path.split(file_path)

                messagebox.showinfo("Download started",
                                    "file is being downloaded "
                                    f"to '{file_path}'."
                                    )
                try:
                    utils.download_fen(
                        url=url,
                        save_path=save_dir,
                        file_name=file_name,
                        base_url=""
                    )
                except Exception:
                    messagebox.showerror("Download failed",
                                         "file could not be downloaded "
                                         f"to '{file_path}'."
                                         )
                    return
                messagebox.showinfo("Download completed",
                                    "file has been downloaded "
                                    f"to '{file_path}'."
                                    )
                self.view.entries["URL"].delete(0, 'end')
        else:
            messagebox.showwarning("Invalid url",
                                   "Please enter a url")
            return

    def select_save_dir(self):
        files = [
            ('Txt Files', '*.txt')
        ]
        file_path = filedialog.asksaveasfile(
            filetypes=files,
            defaultextension=files)
        if not file_path:
            return None
        return file_path.name
