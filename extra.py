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


class SwitchGroup(object):
    def __init__(self, group):
        self.name = group
        self.screenGroupMap = {}

    def __call__(self, qtile):
        log.debug("SwitchGroup:%s:%s", qtile.currentScreen.index, self.name)
        index = int(self.name)
        if qtile.currentScreen.index > 0:
            index = index + 10

        qtile.currentScreen.cmd_togglegroup(str(index))
        #prev_group = self.screenGroupMap.get(qtile.currentScreen.index)
        #if qtile.currentGroup.name == self.name and prev_group:
        #    qtile.currentScreen.cmd_togglegroup(prev_group)
        #else:
        #    self.screenGroupMap[qtile.currentScreen.index] = qtile.currentGroup
        #    qtile.currentScreen.cmd_togglegroup(qtile.groupMap[self.name])


class MoveToOtherScreenGroup(object):
    def __call__(self, qtile):
        otherscreen = (qtile.screens.index(qtile.currentScreen) + 1) \
                      % len(qtile.screens)
        othergroup = qtile.screens[otherscreen].group.name
        qtile.currentWindow.cmd_togroup(othergroup)


class SwitchToWindowGroup(object):
    def __init__(self, name, cmd=None, screen=0):
        self.name = name
        self.cmd = cmd
        self.screen = screen

    def spawn_ifnot(self, qtile):
        log.debug(qtile.currentGroup)
        for window in qtile.windowMap.values():
            if window.group and window.match(wname=self.name):
                return True
        qtile.cmd_spawn(self.cmd)
        return False

    def __call__(self, qtile):
        log.debug("currentScreen:%s", qtile.currentScreen.index)
        log.debug(self.screen)
        if self.screen > len(qtile.screens) - 1:
            self.screen = len(qtile.screens) - 1
        if qtile.currentScreen.index != self.screen:
            qtile.cmd_to_screen(self.screen)
            return
        self.spawn_ifnot(qtile)
        qtile.currentScreen.cmd_togglegroup(self.name)


def check_restart(qtile):
    try:
        for pyfile in glob.glob(os.path.expanduser('~/.config/qtile/*.py')):
            log.debug(pyfile)
            compile(pyfile, doraise=True)
    except Exception as e:
        log.exception("Syntax error")
    else:
        qtile.cmd_restart()


def get_num_monitors():
    #import Xlib.display
    #display = Xlib.display.Display(':0')
    #return display.screen_count()
    output = subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4',shell=True, stdout=subprocess.PIPE).communicate()[0]

    displays = output.strip().split('\n')
    return len(displays)
    #for display in displays:
    #    values = display.split('x')
    #    width = values[0]
    #    height = values[1]
    #    print "Width:" + width + ",height:" + height