import glob
import logging
import os
from os.path import expanduser
from py_compile import compile

from libqtile.config import Group, Match, Rule

from system import execute_once

log = logging.getLogger('myqtile')

# terminal1 = "urxvtc -title term1 -e /home/steven/bin/tmx_outer term1"
_terminal = "st -t {0} "


def terminal_tmux(level, session):
    return "{0} -e {1} {2} {3}".format(
        _terminal.format(session), expanduser("~/.local/bin/tmux.py"), level, session)


def terminal(title, cmd=None):
    term = _terminal.format(title)
    if cmd:
        term += " -e %s" % cmd
    return term


class SwitchGroup(object):
    def __init__(self, group, preferred_screen=None):
        self.name = group
        self.preferred_screen = preferred_screen

    def __call__(self, qtile):
        logging.debug("SwitchGroup:%s:%s", qtile.currentScreen.index, self.name)
        max_screen = len(qtile.screens) - 1
        if(self.preferred_screen is not None and
           self.preferred_screen <= max_screen):
            screen = qtile.screens[self.preferred_screen]
            if self.preferred_screen != qtile.currentScreen.index:
                qtile.cmd_to_screen(self.preferred_screen)
                if qtile.currentGroup.name == self.name:
                    return
        else:
            screen = qtile.currentScreen

        try:
            index = int(self.name)
        except ValueError:
            index = self.name
        else:
            if screen.index >= 0:
                index = index + (screen.index * 10)
            index = str(index)
        log.debug("SwitchGroup: %s", index)

        screen.cmd_togglegroup(index)


class MoveToGroup(object):
    def __init__(self, group):
        self.name = group

    def __call__(self, qtile):
        logging.debug("MoveToGroup:%s:%s", qtile.currentScreen.index, self.name)
        index = int(self.name)
        screenindex = qtile.currentScreen.index
        if screenindex > 0:
            index = index + (screenindex * 10)
        index = str(index)
        qtile.currentWindow.cmd_togroup(index)


def move_to_next_group(qtile):
    index = qtile.groups.index(qtile.currentGroup) + 1
    if len(qtile.groups) == index:
        index = 0
    qtile.currentWindow.cmd_togroup(qtile.groups[index].name)


def move_to_prev_group(qtile):
    index = qtile.groups.index(qtile.currentGroup) - 1
    if index < 0:
        index = len(qtile.groups) - 1
    qtile.currentWindow.cmd_togroup(qtile.groups[index].name)


class MoveToOtherScreenGroup(object):
    def __init__(self, prev=False):
        self.direction = -1 if prev else 1

    def __call__(self, qtile):
        logging.error("MoveToOtherScreenGroup:%s", qtile.currentScreen.index)
        otherscreen = (qtile.screens.index(qtile.currentScreen)
                       + self.direction) % len(qtile.screens)
        othergroup = qtile.screens[otherscreen].group.name
        if qtile.currentWindow:
            qtile.currentWindow.cmd_togroup(othergroup)


class SwitchToWindowGroup(object):
    def __init__(
            self, name, title=None, spawn=None, screen=0, matches=None):
        self.name = name
        self.title = title
        self.cmd = spawn
        self.screen = screen

    def raise_window(self, qtile):
        for window in qtile.windowMap.values():
            if window.group and window.match(wname=self.title):
                qtile.currentGroup.focus(window, False)

    def spawn_ifnot(self, qtile):
        logging.debug(qtile.currentGroup)
        for window in qtile.windowMap.values():
            if window.group and window.match(wname=self.title):
                return True
        qtile.cmd_spawn(self.cmd)
        return False

    def __call__(self, qtile):
        logging.debug("currentScreen:%s", qtile.currentScreen.index)
        logging.debug(self.screen)
        self.spawn_ifnot(qtile)
        if self.screen > len(qtile.screens) - 1:
            self.screen = len(qtile.screens) - 1
        if qtile.currentScreen.index != self.screen:
            qtile.cmd_to_screen(self.screen)
            return
        #self.raise_window(qtile)
        try:
            qtile.currentScreen.cmd_togglegroup(self.name)
        except Exception as e:
            log.exception("wierd")


class RaiseWindowOrSpawn(object):
    def __init__(
            self, wmclass=None, wmname=None, cmd=None, cmd_match=None,
            floating=False, static=False, toggle=False, alpha=0.7):
        self.wmname = wmname
        self.cmd = cmd
        self.cmd_match = cmd_match
        self.wmclass = wmclass
        self.floating = floating
        self.static = static
        self.toggle = toggle
        self.window = None
        self.alpha = 0.7
        if wmname:
            from config import float_windows
            float_windows.append(wmname)

    def __call__(self, qtile):

        for window in qtile.windowMap.values():
            if window.group and window.match(
                    wname=self.wmname, wmclass=self.wmclass):
                #window.cmd_to_screen(qtile.currentScreen.index)
                logging.debug("Match: %s", self.wmname)
                #window.cmd_togroup(qtile.currentGroup.name)
                self.window = window
                break

        if self.window:
            window = self.window
            if self.static and isinstance(self.static, list):
                window.cmd_static(*self.static)
            elif self.floating:
                window.floating = self.floating
            if self.toggle or True:
                if window.hidden:
                    window.unhide()
                else:
                    window.hide()
            logging.error("Hidden: %s %s", window.hidden, window.window.wid)
            execute_once("transet-df %s -i %s" % (self.alpha, window.window.wid))
        logging.error("Current group: %s",qtile.currentGroup.name)
        execute_once(self.cmd, self.cmd_match, qtile=qtile)


def check_restart(qtile):
    logging.info("check_restart qtile ...")
    try:
        for pyfile in glob.glob(os.path.expanduser('~/.config/qtile/*.py')):
            # log.debug(pyfile)
            compile(pyfile, doraise=True)
    except Exception as e:
        logging.exception("Syntax error")
    else:
        #import signal
        #signal.signal(signal.SIGCHLD, signal.SIG_DFL)
        logging.info("restarting qtile ...")
        qtile.cmd_restart()


def list_windows(qtile, current_group=False):
    from sh import dmenu

    def title_format(x):
        return "[%s] %s" % (
            x.group.name if x.group else '',
            x.name)

    if current_group:
        window_titles = [
            w.name for w in qtile.groupMap[qtile.currentGroup.name].windows
            if w.name != "<no name>"
        ]
    else:
        window_titles = [
            title_format(w) for w in qtile.windowMap.values() if w.name != "<no name>"
        ]
    logging.info(window_titles)
    from themes import dmenu_defaults
    dmenu_defaults = dmenu_defaults.replace("'", "").split()

    def process_selected(selected):
        if not current_group:
            group, selected = selected.split(']', 1)
        selected = selected.strip()
        logging.info("Switch to: %s", selected)
        for window in qtile.windowMap.values():
            try:
                #logging.debug("window %s : %s", repr(window.name), repr(selected))
                if window.group and str(window.name) == str(selected):
                    #window.cmd_to_screen(qtile.currentScreen.index)
                    #qtile.cmd_to_screen(window.
                    logging.debug("raise %s:", window.group.screen)
                    if window.group.screen:
                        qtile.cmd_to_screen(window.group.screen.index)
                    else:
                        window.group.cmd_toscreen()
                    #qtile.currentScreen.cmd_togglegroup(window.group.name)
                    return True
            except Exception as e:
                logging.exception("error in group")
        return True

    try:
        s = dmenu(
            "-i", "-p", "%s >>> " % ((
                "[%s]" % qtile.currentGroup.name) if current_group else "[*]"),
            *dmenu_defaults,
            _in="\n".join(window_titles), _out=process_selected)
        s.wait()
    except Exception as e:
        logging.exception("error running dmenu")


def list_windows_group(qtile):
    return list_windows(qtile, current_group=True)


def set_groups(qtile):
    for client in qtile.windowMap.values():
        for rule in qtile.dgroups.rules:
            if rule.matches(client):
                if rule.group:
                    client.togroup(rule.group)
