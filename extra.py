from libqtile.config import Key, Click, Drag, Screen, Group, Match, Rule
from libqtile.command import lazy
from libqtile import layout, bar, widget, hook
from libqtile.dgroups import simple_key_binder
import logging
import subprocess
from py_compile import compile
import re
import os
import glob

log = logging.getLogger("qtile.extra")
log.setLevel(logging.DEBUG)


# terminal1 = "urxvtc -title term1 -e /home/steven/bin/tmx_outer term1"
terminal1 = "st -t %s -e /home/steven/bin/tmx_outer %s"


def terminal(x):
    return terminal1 % (x, x)


class SwitchGroup(CommandObject):
    def __init__(self, group):
        self.group = group
        self.prev_group = None

    def __call__(self, qtile):
        if qtile.currentGroup == qtile.groupMap[self.group]\
           and self.prev_group:
            qtile.currentScreen.setGroup(self.prev_group)
        else:
            self.prev_group = qtile.currentGroup
            qtile.currentScreen.setGroup(qtile.groupMap[self.group])


class SwitchToWindowGroup(object):
    def __init__(self, name, cmd=None, screen=0):
        self.name = name
        self.cmd = cmd
        self.screen = screen

    def _switchto(self, qtile):
        for window in qtile.windowMap.values():
            if window.group and window.match(wname=self.name):
                if window.group == qtile.currentGroup:
                    qtile.screens[self.screen].cmd_togglegroup()
                else:
                    qtile.screens[self.screen].setGroup(window.group)
                    window.group.focus(window, False)
                return True
        return False

    def __call__(self, qtile):
        log.debug("currentScreen:%s", qtile.currentScreen.index)
        log.debug(self.screen)
        if self.screen > len(qtile.screens) - 1:
            self.screen = len(qtile.screens) - 1
        if qtile.currentScreen.index != self.screen:
            qtile.cmd_to_screen(self.screen)
            return
        found = self._switchto(qtile)
        if not found and self.cmd:
            qtile.cmd_spawn(self.cmd)
            self._switchto(qtile)


def check_restart(qtile):
    try:
        for pyfile in glob.glob(os.path.expanduser('~/.config/qtile/*.py')):
            compile(pyfile, doraise=True)
    except Exception as e:
        log.exception("Syntax error")
    else:
        qtile.cmd_restart()
