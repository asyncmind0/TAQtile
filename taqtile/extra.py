import glob
import six
import logging
import os
from libqtile.config import (
    Key,
    Group,
    Match,
    ScratchPad,
    DropDown,
)
from os.path import expanduser, isdir, join, pathsep
from py_compile import compile
from subprocess import check_output
import re
from taqtile.themes import current_theme
from taqtile.system import (
    execute_once,
    window_exists,
    get_hostconfig,
    get_current_screen,
    get_current_window,
    get_current_group,
    get_windows_map,
    group_by_name,
)
from time import sleep
from threading import Thread
from libqtile.command import lazy
from libqtile.utils import send_notification

import logging

logger = logging.getLogger(__name__)


# terminal1 = "urxvtc -title term1 -e /home/steven/bin/tmx_outer term1"
# _terminal = "alacritty -t {0} "
def get_terminal_command(
    title="st",
    window_class="st",
    terminal_font=current_theme.get("terminal_font", None),
    terminal_fontsize=current_theme.get("terminal_fontsize", None),
):
    return f'st -f "{terminal_font}:pixelsize={terminal_fontsize}" -t "{title}" -c {window_class} '


# _terminal = "alacritty -t {0} "
# _terminal = "kitty --name {0} --title {0} "


def terminal_tmux(level, session):
    return "systemd-run --user {0} -e {1} -w {2} -c {3} {4} {5}".format(
        get_terminal_command(title=session),
        expanduser("~/.local/bin/tmux.py"),
        expanduser("~/.tmux/configs/default.yml"),
        expanduser("~/.tmux/outer.conf"),
        level,
        session,
    )


def terminal(title, window_class="st", cmd=None):
    term = get_terminal_command(title=title, window_class=window_class)
    if cmd:
        term += "-e %s" % cmd
    logger.info(f"starting terminal: {term}")
    return term


class SwitchToScreen(object):
    def __init__(self, group, preferred_screen=None):
        self.name = group
        self.preferred_screen = preferred_screen

    def __call__(self, qtile):
        max_screen = len(qtile.screens) - 1
        if (
            self.preferred_screen is not None
            and self.preferred_screen <= max_screen
        ):
            screen = qtile.screens[self.preferred_screen]
            if self.preferred_screen != get_current_screen(qtile).index:
                qtile.to_screen(self.preferred_screen)
                if get_current_group(qtile).name == self.name:
                    return
        else:
            screen = get_current_screen(qtile)

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
        screen, index = super().__call__(qtile)
        if index and screen:
            screen.toggle_group(index)


class SwitchToScreenGroupUrgent(SwitchToScreenGroup):
    def __call__(self, qtile):
        super().__call__(qtile)
        cg = get_current_group(qtile)
        for group in qtile.group_map.values():
            if group == cg:
                continue
            if len([w for w in group.windows if w.urgent]) > 0:
                get_current_screen(qtile).setGroup(group)
                return


class MoveToGroup(object):
    def __init__(self, group):
        self.name = group

    def __call__(self, qtile):
        logging.debug(
            "MoveToGroup:%s:%s", get_current_screen(qtile).index, self.name
        )
        index = int(self.name)
        screenindex = get_current_screen(qtile).index
        if screenindex > 0:
            index = index + (screenindex * 10)
        index = str(index)
        get_current_window(qtile).togroup(index)


def move_to_next_group(qtile):
    index = qtile.groups.index(get_current_group(qtile)) + 1
    if len(qtile.groups) == index:
        index = 0
    get_current_window(qtile).togroup(qtile.groups[index].name)


def move_to_prev_group(qtile):
    index = qtile.groups.index(get_current_group(qtile)) - 1
    if index < 0:
        index = len(qtile.groups) - 1
    get_current_window(qtile).togroup(qtile.groups[index].name)


class MoveToOtherScreenGroup(object):
    def __init__(self, prev=False):
        self.direction = -1 if prev else 1

    def __call__(self, qtile):
        logger.error(
            "MoveToOtherScreenGroup:%s", get_current_screen(qtile).index
        )
        otherscreen = (
            qtile.screens.index(get_current_screen(qtile)) + self.direction
        ) % len(qtile.screens)
        othergroup = qtile.screens[otherscreen].group.name
        if get_current_window(qtile):
            get_current_window(qtile).togroup(othergroup)


class SwitchToWindowGroup(object):
    def __init__(self, name, title=None, spawn=None, screen=0, matches=None):
        self.name = name
        self.title = (
            re.compile(title) if isinstance(title, six.string_types) else title
        )
        self.screen = screen
        if spawn:
            self.cmd = spawn if isinstance(spawn, (tuple, list)) else [spawn]
        else:
            self.cmd = []

    def raise_window(self, qtile):
        for window in get_windows_map(qtile).values():
            if window.group and window.match(Match(title=self.title)):
                logger.debug("Raise window %s", window)
                get_current_group(qtile).focus(window, False)

    def spawn_ifnot(self, qtile):
        cmds = []
        try:
            for cmd in self.cmd:
                if isinstance(cmd, dict):
                    if not window_exists(qtile, re.compile(cmd["match"])):
                        cmds.append(cmd["cmd"])
                else:
                    if not window_exists(qtile, self.title):
                        cmds.append(cmd)
            for cmd in cmds:
                logger.info("Spawn %s", cmd)
                qtile.spawn(f"systemd-run --user {cmd}")
        except Exception as e:
            logger.exception("wierd")
        return False

    def __call__(self, qtile):
        logger.debug(f"spawn cmd: {self.cmd}")
        self.spawn_ifnot(qtile)
        if self.screen > len(qtile.screens) - 1:
            self.screen = len(qtile.screens) - 1
        if get_current_screen(qtile).index != self.screen:
            qtile.to_screen(self.screen)
        else:
            get_current_screen(qtile).toggle_group(self.name)
        self.raise_window(qtile)


class ToggleApplication(SwitchToWindowGroup):
    def __call__(self, qtile):
        self.spawn_ifnot(qtile)


class RaiseWindowOrSpawn(object):
    def __init__(
        self,
        wmclass=None,
        wmname=None,
        cmd=None,
        cmd_match=None,
        floating=False,
        static=False,
        toggle=False,
        alpha=1,
    ):
        self.wmname = wmname
        self.cmd = cmd
        self.cmd_match = cmd_match
        self.wmclass = wmclass
        self.floating = floating
        self.static = static
        self.toggle = toggle
        self.window = None
        self.alpha = alpha
        # if wmname:
        #    from config import float_windows
        #    float_windows.append(wmname)
        assert self.static in [False, None] or isinstance(
            self.static, (list, tuple)
        )

    def __call__(self, qtile):
        execute_once(
            self.cmd, process_filter=self.cmd_match, qtile=qtile, toggle=True
        )

        for window in get_windows_map(qtile).values():
            if window.group and window.match(
                wname=self.wmname, wmclass=self.wmclass
            ):
                # window.cmd_to_screen(get_current_screen(qtile).index)
                logger.debug("Match: %s", self.wmname)
                window.togroup(get_current_group(qtile).name)
                self.window = window
                break

        if self.window:
            window = self.window
            # if self.static:
            #    window.static(*self.static)
            if self.toggle or True:
                if window.hidden:
                    window.unhide()
                    logger.error("Window: %s", window.info()["id"])
                else:
                    window.hide()
            if self.floating:
                window.floating = self.floating
            # execute_once(
            #    "transet-df -n %s %s " % (window.name, self.alpha), qtile=qtile
            # )

        logger.debug("No window found spawning: %s", self.cmd)


def check_restart(qtile):
    logger.info("check_restart qtile ...")
    try:
        for pyfile in glob.glob(os.path.expanduser("~/.config/qtile/*.py")):
            # log.debug(pyfile)
            compile(pyfile, doraise=True)
    except Exception as e:
        logger.exception("Syntax error")
    else:
        # import signal
        # signal.signal(signal.SIGCHLD, signal.SIG_DFL)
        logger.info("restarting qtile ...")
        qtile.restart()


def autossh_term(title="autossh", port=22, host="localhost", session="default"):
    autossh_py = "autossh.py"
    cmd = " ".join(
        [
            "st",
            # "alacritty",
            "-t",
            title,
            "-e",
            autossh_py,
            "%s:%s" % (host, port),
            "outer",
            title,
        ]
    )
    return cmd


def show_mail(qtile):
    from collections import OrderedDict
    import notmuch

    queries = OrderedDict()
    queries[
        "inbox"
    ] = "(tag:INBOX or tag:inbox) and not (tag:misc) and date:30d..0s and tag:unread and tag:me"
    queries["pullrequests"] = "tag:pullrequests and tag:unread"
    queries["drafts"] = "tag:draft"
    queries["Other"] = "tag:INBOX and tag:unread"
    try:
        db = notmuch.Database()
        message = []
        for mbox, query in queries.items():
            query = db.create_query(query)
            message.append("%s: %s" % (mbox, query.count_messages()))
        send_notification(
            "Mail",
            "<br>".join(message),
            # icon=user_icon
        )
    except Exception:
        logger.exception("Error querying notmuch")


def hide_show_bar(qtile):
    def timer():
        qtile.hide_show_bar()
        sleep(1)
        qtile.hide_show_bar()

    Thread(None, timer).start()


class Terminal:
    def __init__(
        self,
        name,
        key,
        group=None,
        screen=None,
        groups=None,
        keys=None,
        dgroups=None,
        spawn=None,
    ):
        self.name = name
        self.key = key
        self.group = group or name
        self.screen = screen or 0
        self.spawn = spawn or terminal_tmux("outer", self.name)
        keys.append(self.get_keybinding())
        groups.append(self.get_group())
        dgroups.append(self.get_dgroup_match())

    def get_keybinding(self):
        mod = []
        key = None
        if isinstance(self.key, (list, tuple)) and len(self.key) == 2:
            mod, key = self.key
        else:
            key = self.key
        return Key(
            mod,
            key,
            lazy.function(
                SwitchToWindowGroup(
                    self.name,
                    title=self.name,
                    screen=self.screen,
                    spawn=self.spawn,
                )
            ),
        )

    def get_match(self):
        return Match(title=[self.name])

    def get_group(self):
        return Group(
            self.name,
            screen_affinity=self.screen,
            exclusive=False,
            init=True,
            # layout="max",
            matches=[self.get_match()],
        )

    def get_dgroup_match(self):
        from taqtile.groups import Rule

        return Rule(
            self.get_match(),
            group=self.group,
            fullscreen=False,
            float=False,
        )


def float_to_front(qtile):
    """
    Bring all floating windows of the group to front
    """
    global floating_windows
    floating_windows = []
    for window in qtile.windows_map.values():
        if getattr(window, "floating", False):
            window.bring_to_front()
            floating_windows.append(window)
    floating_windows[-1].focus()
