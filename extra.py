from libqtile.config import Group, Match
import logging
import subprocess
from py_compile import compile
import os
import glob

log = logging.getLogger("qtile.extra")
log.setLevel(logging.DEBUG)


# terminal1 = "urxvtc -title term1 -e /home/steven/bin/tmx_outer term1"
terminal1 = "st -t %s -e tmx_outer %s"


def terminal(x):
    return terminal1 % (x, x)


class SwitchGroup(object):
    def __init__(self, group, preferred_screen=None):
        self.name = group
        self.preferred_screen = preferred_screen

    def __call__(self, qtile):
        log.debug("SwitchGroup:%s:%s", qtile.currentScreen.index, self.name)
        max_screen = len(qtile.screens) - 1
        if (self.preferred_screen is not None and
            self.preferred_screen <= max_screen):
            screen = qtile.screens[self.preferred_screen]
            if self.preferred_screen != qtile.currentScreen.index:
                qtile.cmd_to_screen(self.preferred_screen)
                if qtile.currentGroup.name == self.name:
                    return
        else:
            screen = qtile.currentScreen

        index = int(self.name)
        if screen.index > 0:
            index = index + (screen.index * 10)
        index = str(index)

        screen.cmd_togglegroup(index)


class MoveToGroup(object):
    def __init__(self, group):
        self.name = group

    def __call__(self, qtile):
        log.debug("MoveToGroup:%s:%s", qtile.currentScreen.index, self.name)
        index = int(self.name)
        screenindex = qtile.currentScreen.index
        if screenindex > 0:
            index = index + (screenindex * 10)
        index = str(index)
        qtile.currentWindow.cmd_togroup(index)


class MoveToOtherScreenGroup(object):
    def __init__(self, prev=False):
        self.direction = -1 if prev else 1

    def __call__(self, qtile):
        otherscreen = (qtile.screens.index(qtile.currentScreen)
                       + self.direction) % len(qtile.screens)
        othergroup = qtile.screens[otherscreen].group.name
        qtile.currentWindow.cmd_togroup(othergroup)


class SwitchToWindowGroup(object):
    def __init__(
            self, groups, name, title=None, cmd=None, screen=0, wm_class=None,
            exclusive=False):
        self.name = name
        self.cmd = cmd
        self.screen = screen
        groups.append(Group(name, exclusive=exclusive, spawn=cmd,
                            matches=[Match(title=title, wm_class=wm_class)]))

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
    log.info("check_restart qtile ...")
    try:
        for pyfile in glob.glob(os.path.expanduser('~/.config/qtile/*.py')):
            # log.debug(pyfile)
            compile(pyfile, doraise=True)
    except Exception as e:
        log.exception("Syntax error")
    else:
        import signal
        signal.signal(signal.SIGCHLD, signal.SIG_DFL)
        log.info("restarting qtile ...")
        qtile.cmd_restart()


