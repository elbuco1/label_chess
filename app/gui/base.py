import tkinter as tk
import abc


class Controller(abc.ABC):
    @abc.abstractmethod
    def bind_view(self, view):
        raise NotImplementedError


class View(tk.Frame):
    @abc.abstractmethod
    def create_view(self):
        raise NotImplementedError


class ButtonsMixin():
    def __init__(self):
        self.buttons = {}

    def activate_button(self, name):
        self.buttons[name]["state"] = "normal"

    def disable_button(self, name):
        self.buttons[name]["state"] = "disabled"
