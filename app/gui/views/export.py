import tkinter as tk
from tkinter import simpledialog

from app.gui.base import View


class ExportDialog(simpledialog.Dialog):
    def __init__(self, parent, title, options):
        self.options = options
        self.check_boxes = {}
        self.vars = {}
        super().__init__(parent, title)

    def body(self, frame):
        self.container = tk.LabelFrame(master=frame, text="Annotations")
        self.container.pack(fill=tk.BOTH)

        for option in self.options:
            self.vars[option] = tk.IntVar()
            self.check_boxes[option] = tk.Checkbutton(self.container, text=option,
                                                      variable=self.vars[option])
            self.check_boxes[option].pack(fill=tk.BOTH)

        return frame

    def ok_pressed(self):
        self.checks = [k for k, v in self.vars.items() if v.get() == 1]
        self.destroy()

    def cancel_pressed(self):
        self.destroy()

    def buttonbox(self):
        self.ok_button = tk.Button(
            self, text='Export', width=5, command=self.ok_pressed)
        self.ok_button.pack(side="left")
        cancel_button = tk.Button(
            self, text='Cancel', width=5, command=self.cancel_pressed)
        cancel_button.pack(side="right")
        self.bind("<Return>", lambda event: self.ok_pressed())
        self.bind("<Escape>", lambda event: self.cancel_pressed())


def export_dialog(parent=None, options=[]):
    dialog = ExportDialog(title="Export annotations",
                          parent=parent, options=options)
    return dialog.checks
