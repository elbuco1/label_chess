import tkinter as tk
import abc


class Controller(abc.ABC):
    @abc.abstractmethod
    def bind_view(self, view: View):
        raise NotImplementedError
