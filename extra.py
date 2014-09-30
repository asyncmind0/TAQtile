import glob
import logging
import os
from py_compile import compile

from libqtile.config import Group, Match, Rule

from system import execute_once


# terminal1 = "urxvtc -title term1 -e /home/steven/bin/tmx_outer term1"
terminal1 = "st -t %s -e tmx_outer %s"


def terminal(x):
    return terminal1 % (x, x)


class SwitchGroup(object):
    def __init__(self, group, preferred_screen=None):
        self.name = group
        self.preferred_screen = preferred_screen

    def __call__(self, qtile):
        logging.debug("SwitchGroup:%s:%s", qtile.currentScreen.index, self.name)
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

        try:
            index = int(self.name)
        except ValueError:
            index = self.name
        else:
            if screen.index > 0:
                index = index + (screen.index * 10)
            index = str(index)

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
            exclusive=False, dynamic_groups_rules=None):
        self.name = name
        self.cmd = cmd
        self.screen = screen
        groups.append(Group(name, exclusive=exclusive, spawn=cmd,
                            matches=[Match(title=title, wm_class=wm_class)]))
        if dynamic_groups_rules:
            dynamic_groups_rules.append(Rule(Match(title=title), group=name))

    def raise_window(self, qtile):
        for window in qtile.windowMap.values():
            if window.group and window.match(wname=self.name):
                qtile.currentGroup.focus(window, False)

    def spawn_ifnot(self, qtile):
        logging.debug(qtile.currentGroup)
        for window in qtile.windowMap.values():
            if window.group and window.match(wname=self.name):
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
        qtile.currentScreen.cmd_togglegroup(self.name)


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
    if current_group:
        window_titles = [
            w.name for w in  qtile.groupMap[qtile.currentGroup.name].windows
            if w.name != "<no name>"]
    else:
        window_titles = [w.name for w in qtile.windowMap.values() if w.name != "<no name>"]
    logging.info(window_titles)
    from themes import dmenu_defaults
    dmenu_defaults = dmenu_defaults.replace("'", "").split()

    def process_selected(selected):
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
            "-i", "-p", ">>> ",
            *dmenu_defaults,
            _in="\n".join(window_titles), _out=process_selected)
        s.wait()
    except Exception as e:
        logging.exception("error running dmenu")


def list_windows_group(qtile):
    return list_windows(qtile, current_group=True)
