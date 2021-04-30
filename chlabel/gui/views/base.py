import tkinter as tk
import abc


class View(tk.Frame):
    @abc.abstractmethod
    def create_view(self):
        raise NotImplementedError
