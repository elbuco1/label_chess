import tkinter as tk


class View(tk.Frame):
    @abc.abstractmethod
    def create_view(self):
        raise NotImplementedError
