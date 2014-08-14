from libqtile.config import Key, Click, Drag, Screen, Group, Match, Rule
from libqtile.command import lazy
from libqtile import layout, bar, widget, hook
from libqtile.dgroups import simple_key_binder
import logging as log
import subprocess
from py_compile import compile
import re
import os


default_theme = dict(
    fontsize=14,
    padding=0,
    borderwidth=1,
    font="Inconsolata"
)

star_trek_blue = dict(
    border="#42B1FF",
    foreground="#06B4E7",
    background="#010F2C",
)

matrix_green = dict(
    border="#1AF03E",
    border_focus="#1AF03E",
    foreground="#00FD00",
    background="#125B29",
    borderwidth=2,
)

current_theme = dict(default_theme)
current_theme.update(matrix_green)
log.debug("Current theme:%s", current_theme)
#current_theme = matrix_green
dmenu_defaults = (
    "-w -f -l 40 "
    "-nb black -nf white "
    "-sb '%(background)s' -sf '%(foreground)s' "
    "-fn %(font)s"
) % current_theme
