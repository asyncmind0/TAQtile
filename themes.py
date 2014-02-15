from libqtile.config import Key, Click, Drag, Screen, Group, Match, Rule
from libqtile.command import lazy
from libqtile import layout, bar, widget, hook
from libqtile.dgroups import simple_key_binder
import logging
import subprocess
from py_compile import compile
import re
import os
log = logging.getLogger("qtile.themes")

star_trek_blue = dict(
    border="#42B1FF",
    foreground="#06B4E7",
    background="#010F2C",
    font="terminus"
)

matrix_green = dict(
    border="#00FD00",
    foreground="#00FD00",
    background="#125B29",
    font="terminus"
)

current_theme = star_trek_blue
current_theme = matrix_green
