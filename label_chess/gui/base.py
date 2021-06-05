#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc

import tkinter as tk


class Controller(abc.ABC):
    """Abstract base class for all the controllers
    of the app. Controllers implement only the logic and
    must be paired with a view.
    """
    @abc.abstractmethod
    def bind_view(self, view):
        raise NotImplementedError


class View(tk.Frame):
    """Abstract base class for all the views
    of the app. Views implement only the front end and
    must be paired with a controller.
    """
    @abc.abstractmethod
    def create_view(self):
        raise NotImplementedError


class ButtonsMixin():
    """Provides two methods that can be used
    to activate/deactivate any button of tkinter
    object
    """

    def __init__(self):
        self.buttons = {}

    def activate_button(self, name):
        self.buttons[name]["state"] = "normal"

    def disable_button(self, name):
        self.buttons[name]["state"] = "disabled"
