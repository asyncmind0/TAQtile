import glob
import six
import logging
import os
from os.path import expanduser, isdir, join, pathsep
from py_compile import compile
from subprocess import check_output
import re
from system import execute_once, window_exists

from log import logger
try:
    import notify2
except:
    pass


# terminal1 = "urxvtc -title term1 -e /home/steven/bin/tmx_outer term1"
_terminal = "st -t {0} "


def terminal_tmux(level, session):
    return "{0} -e {1} {2} {3}".format(
        _terminal.format(session),
        expanduser("~/.local/bin/tmux.py"),
        level,
        session
    )


def terminal(title, cmd=None):
    term = _terminal.format(title)
    if cmd:
        term += " -e %s" % cmd
    return term


class SwitchToScreen(object):
    def __init__(self, group, preferred_screen=None):
        self.name = group
        self.preferred_screen = preferred_screen

    def __call__(self, qtile):
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
        return screen, index


class SwitchToScreenGroup(SwitchToScreen):
    def __call__(self, qtile):
        screen, index = super(SwitchToScreenGroup, self).__call__(qtile)
        if index and screen:
            screen.cmd_toggle_group(index)


class SwitchToScreenGroupUrgent(SwitchToScreenGroup):
    def __call__(self, qtile):
        screen, index = super(SwitchToScreenGroupUrgent, self).__call__(qtile)
        cg = qtile.currentGroup
        for group in qtile.groupMap.values():
            if group == cg:
                continue
            if len([w for w in group.windows if w.urgent]) > 0:
                qtile.currentScreen.setGroup(group)
                return


class MoveToGroup(object):
    def __init__(self, group):
        self.name = group

    def __call__(self, qtile):
        logging.debug(
            "MoveToGroup:%s:%s", qtile.currentScreen.index, self.name)
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
        logger.error("MoveToOtherScreenGroup:%s", qtile.currentScreen.index)
        otherscreen = (qtile.screens.index(qtile.currentScreen)
                       + self.direction) % len(qtile.screens)
        othergroup = qtile.screens[otherscreen].group.name
        if qtile.currentWindow:
            qtile.currentWindow.cmd_togroup(othergroup)


class SwitchToWindowGroup(object):
    def __init__(
            self, name, title=None, spawn=None, screen=0, matches=None):
        self.name = name
        self.title = re.compile(title) if isinstance(title, six.string_types) else title
        self.screen = screen
        if spawn:
            self.cmd = spawn if isinstance(spawn, (tuple, list)) else [spawn]
        else:
            self.cmd = []

    def raise_window(self, qtile):
        for window in qtile.windowMap.values():
            if window.group and window.match(wname=self.title):
                logger.debug("Raise window %s", window)
                qtile.currentGroup.focus(window, False)

    def spawn_ifnot(self, qtile):
        cmds = []
        try:
            for cmd in self.cmd:
                logger.debug("Spawn %s", cmd)
                if isinstance(cmd, dict):
                    if not window_exists(qtile, cmd['match']):
                        cmds.append(cmd['cmd'])
                else:
                    if not window_exists(qtile, self.title):
                        cmds.append(cmd)
            for cmd in cmds:
                logger.debug(cmd)
                qtile.cmd_spawn(cmd)
                return True
        except Exception as e:
            logger.exception("wierd")
        return False

    def __call__(self, qtile):
        self.spawn_ifnot(qtile)
        if self.screen > len(qtile.screens) - 1:
            self.screen = len(qtile.screens) - 1
        if qtile.currentScreen.index != self.screen: # and qtile.currentWindow.title != self.title:
            qtile.cmd_to_screen(self.screen)
        # TODO if target window exists in current group raise it and exit
        # elif qtile.currentWindow.title :
        else:
            try:
                qtile.currentScreen.cmd_toggle_group(self.name)
            except Exception as e:
                logger.exception("wierd")
        self.raise_window(qtile)


class ToggleApplication(SwitchToWindowGroup):
    def __call__(self, qtile):
        self.spawn_ifnot(qtile)



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
                logger.debug("Match: %s", self.wmname)
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
            logger.error("Hidden: %s %s", window.hidden, window.window.wid)
            execute_once(
                "transet-df %s -i %s" % (self.alpha, window.window.wid),
                qtile=qtile
            )
        logger.error("Current group: %s", qtile.currentGroup.name)
        execute_once(self.cmd, process_filter=self.cmd_match, qtile=qtile)


def check_restart(qtile):
    logger.info("check_restart qtile ...")
    try:
        for pyfile in glob.glob(os.path.expanduser('~/.config/qtile/*.py')):
            # log.debug(pyfile)
            compile(pyfile, doraise=True)
    except Exception as e:
        logger.exception("Syntax error")
    else:
        #import signal
        #signal.signal(signal.SIGCHLD, signal.SIG_DFL)
        logger.info("restarting qtile ...")
        qtile.cmd_restart()


def autossh_term(
        title="autossh", port=22, host='localhost',
        session="default"):
    autossh_py = "/home/steven/.local/bin/autossh.py"
    cmd = " ".join(
        [
            "st",
            "-t",
            title,
            "-e",
            autossh_py,
            "%s:%s" % (host, port),
            "outer",
            title
        ]
    )
    return cmd


def show_mail(qtile):
    from collections import OrderedDict
    import notmuch
    queries = OrderedDict()
    queries["inbox"] = "(tag:INBOX or tag:inbox) and not (tag:misc) and date:30d..0s and tag:unread and tag:me"
    queries["pullrequests"] = "tag:pullrequests and tag:unread"
    queries["drafts"] = "tag:draft"
    queries["Other"] = "tag:INBOX and tag:unread"
    try:
        db = notmuch.Database()
        message = []
        for mbox, query in queries.items():
            query = db.create_query(query)
            message.append("%s: %s" % (mbox, query.count_messages()))
        notification = notify2.Notification(
            "Mail",
            "<br>".join(message),
            #icon=user_icon
        )
        notification.show()
    except Exception as e:
        logger.exception("Error querying notmuch")


def start_inboxes(qtile):
    inboxes = {
        'google-chrome-stable --app="https://inbox.google.com/u/0/"': r"^Inbox .* melit.stevenjoseph@gmail.com$",
        'google-chrome-stable --app="https://inbox.google.com/u/1/"': r"^Inbox .* steven@streethawk.co$",
        'google-chrome-stable --app="https://inbox.google.com/u/2/"': r"^Inbox .* stevenjose@gmail.com$",
        'google-chrome-stable --app="https://inbox.google.com/u/3/"': r"^Inbox .* steven@stevenjoseph.in$",
    }
    for inbox, regex in inboxes.items():
        for window in qtile.cmd_windows():
            if re.match(regex, window['name']):
                continue
            else:
                qtile.spawn(inbox)
