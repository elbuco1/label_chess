import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
import shutil

from app.gui import models
from app.gui.base import Controller


class LoaderController(Controller):
    def __init__(self,
                 data_type, db_dir, add_name="",
                 file_type=("All Files", "*.*")):
        """Add the logic to the LoaderView view.

        It is intended to select a file on disk (video, txt),
        join an optional attribute and save it to database.

        This class implements only the back end, no widgets should
        be implemented here.

        Args:
            data_type (models.*): A class in app.gui.models that represents
                an object in the database. For instance: models.Video
            db_dir (str): path to the database directory for the given data type
            add_name (str, optional): must match LoaderView.add_name. Defaults to "".
            file_type (tuple, optional): File type to pass to the askdir
                dialog to limit the type of file that can be selected.
                Defaults to ("All Files", "*.*").
        """
        self.view = None
        self.data_type = data_type
        self.db_dir = db_dir
        self.add_name = add_name
        self.file_type = file_type

    def bind_view(self, view):
        """Link a view to this controller.

        Args:
            view (app.gui.base.View)
        """
        # link a view
        self.view = view
        # create view's widgets
        self.view.create_view()
        # bind methods to some of the view's buttons
        self.view.buttons[f"select_{self.add_name}"].configure(
            command=self.select)
        self.view.buttons["Add"].configure(command=self.add_db)

    def select(self):
        """Open a dialog to select a file on disk,
        then display the selected path in a label on the view.
        """
        self.path = filedialog.askopenfilename(
            filetypes=[self.file_type]
        )
        if not self.path:
            return
        label = self.view.labels[f"select_{self.add_name}"]
        label.configure(
            text=os.path.split(self.path)[-1])

    def add_db(self):
        """Add a file to the database based on the 
        path selected in select.
        """
        # check a file is selected
        if not self.path:
            messagebox.showwarning(
                f"Please select a {self.add_name} on your computer")
            return

        # url is optional. if not sets, defaults to the
        # video path on disk
        url = self.view.entries["URL"].get()
        if url == "":
            url = self.path

        name = os.path.split(self.path)[-1]
        name = name.replace(" ", "_").lower()

        # check if a file with the same filename already is
        # in the database
        if self.exists_in_db(url, name):
            messagebox.showwarning("Already exists",
                                   f"{self.add_name} "
                                   "already exists in database")
            return

        db_path = os.path.join(models.VIDEO_DATA_DIR,
                               name)

        # add file to database
        new_obj = self.data_type(
            url=url,
            original_path=self.path,
            path=db_path,
            name=name)

        self.persist(new_obj,
                     original_path=self.path,
                     db_path=db_path)

        messagebox.showinfo(f"{self.add_name}",
                            f"{self.add_name} successfully added to database.")

        # empty entry and label widgets
        self.view.entries["URL"].delete(0, 'end')
        label = self.view.labels[f"select_{self.add_name}"]
        label.configure(text="")

    def exists_in_db(self, url, name):
        """Check if file url or name is already
        in database.

        Args:
            url (str)
            name (str)
        """
        db = models.get_db()
        urls = db.query(self.data_type.url).all()
        names = db.query(self.data_type.name).all()

        urls = {e[0] for e in urls}
        names = {e[0] for e in names}

        return url in urls or name in names

    def persist(self, obj, original_path, db_path):
        """Add file object to db.
        Copy file to app storage.

        Args:
            obj (models.*): ORM object
            original_path (str): path to the video file
            db_path (str): path where to copy the video
                file.
        """
        shutil.copy(original_path, db_path)
        db = models.get_db()
        db.add(obj)
        db.commit()


class VideoLoaderController(LoaderController):
    def __init__(self):
        """Inherits from LoaderController and fix the
        arguments so that it can be used to add a video
        to the database.
        """
        super().__init__(
            data_type=models.Video,
            db_dir=models.VIDEO_DATA_DIR,
            add_name="video",
            file_type=("MP4 Files", "*.mp4"))


class PGNLoaderController(LoaderController):
    def __init__(self):
        """Inherits from LoaderController and fix the
        arguments so that it can be used to add a PGN file
        to the database.
        """
        super().__init__(
            data_type=models.PGN,
            db_dir=models.PGN_DATA_DIR,
            add_name="pgn",
            file_type=("PGN Files", "*.pgn"))
