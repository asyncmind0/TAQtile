import os
import logging
import re
from datetime import datetime
from functools import lru_cache
from getpass import getuser
from os.path import dirname, join, splitext, expanduser, isdir, pathsep
from subprocess import Popen
import subprocess
from urllib.parse import quote_plus

from libqtile import hook
from libqtile.extension.dmenu import Dmenu, DmenuRun

from libqtile.extension.window_list import WindowList as QWindowList
from libqtile.scratchpad import ScratchPad

from libqtile.backend import base

# from libqtile.extension.window_list import WindowList
from plumbum import local

from taqtile.recent_runner import RecentRunner
from taqtile.system import (
    get_current_window,
    get_hostconfig,
    window_exists,
    get_current_screen,
    get_current_group,
    get_redis,
)
from taqtile.groups import Rule, Match
from taqtile.widgets.obscontrol import obs_pause_recording, obs_resume_recording
from taqtile import sounds
from taqtile.extra import (
    check_restart,
)

logger = logging.getLogger(__name__)


@hook.subscribe.client_new
def set_timestamp(window):
    window.window.set_property(
        "QTILE_CREATED", int(datetime.now().timestamp()), type="ATOM", format=32
    )


def bring_to_top(qtile, current_window):
    if current_window is not None:
        current_group = qtile.current_group
        current_group.windows.remove(current_window)
        current_group.windows.append(current_window)
        current_group.focus(current_window)
        qtile.current_screen.group.layout_all()


class WindowList(QWindowList):
    show_icons = True

    def __init__(self, **config):
        config["markup"] = True
        super().__init__(**config)

    def _configure(self, qtile):
        super()._configure(qtile)
        # insert as second item in the list
        # self.configured_command.insert(1, "-markup")
        if self.show_icons:
            self.configured_command.insert(1, "-show-icons")
            self.configured_command.insert(2, "-icon-theme")
            self.configured_command.insert(3, "breeze-dark")
        logger.debug(f"configured_command: {self.configured_command}")

    def format_item(self, win, key):
        icon = ""
        wmclass = win.window.get_wm_class()
        if wmclass and wmclass[0] == "st":
            icon = "utilities-terminal"
        elif wmclass:
            icon = wmclass[0].lower()
        return f" {key}\0icon\x1f{icon}"

    def run(self):
        self.list_windows()
        window_list = []
        for key, win in self.item_to_win.items():
            created = win.window.get_property(
                "QTILE_CREATED", type="ATOM", unpack=int
            )
            if created:
                created = created[0]
            window_list.append((created, self.format_item(win, key)))
        prompt = self.configured_command[
            self.configured_command.index("-p") + 1
        ]
        self.configured_command[
            self.configured_command.index("-p") + 1
        ] = "[%s]:" % (len(window_list))
        sounds.play_effect("window_list")
        out = Dmenu.run(
            self,
            items=[
                x[-1]
                for x in sorted(window_list, key=lambda x: x[0], reverse=True)
            ],
        )

        try:
            sout = [x.strip() for x in out.split("\n") if x.strip()]
            if len(sout) > 1:
                out = Dmenu.run(
                    self,
                    items=["kill", "move to group"],
                ).strip()
                if out == "kill":
                    for win in sout:
                        win = self.item_to_win[win]
                        win.kill()
                return
            elif sout and len(sout) == 1:
                sout = sout[0]
            else:
                return

        except AttributeError:
            # out is not a string (for example it's a Popen object returned
            # by super(WindowList, self).run() when there are no menu items to
            # list
            return

        try:
            win = self.item_to_win[sout]
        except KeyError:
            # The selected window got closed while the menu was open?
            logger.warning("no window found %s" % sout)
            return
        logger.debug(
            f"window found {win} {win.group}: {self.qtile.current_group}"
        )

        if self.qtile.current_group.name != win.group.name:
            screen = self.qtile.current_screen
            screen.set_group(win.group)
        bring_to_top(self.qtile, win)
        # win.bring_to_front()
        # win.group.focus(win, force=True)
        # win.cmd_focus()


@lru_cache()
def list_executables(ttl_hash=None):
    del ttl_hash
    logger.error("getting execs")
    paths = os.environ["PATH"].split(pathsep)
    executables = []
    for path in filter(isdir, paths):
        for file_ in os.listdir(path):
            if os.access(join(path, file_), os.X_OK):
                executables.append(file_)
    return set(executables)


class KillWindows(Dmenu):
    defaults = [
        (
            "item_format",
            "{group}.{id}: {window}",
            "the format for the menu items",
        ),
        (
            "all_groups",
            True,
            "If True, list windows from all groups; otherwise only from the current group",
        ),
        ("dmenu_lines", "80", "Give lines vertically. Set to None get inline"),
    ]

    def __init__(self, **config):
        Dmenu.__init__(self, **config)
        self.add_defaults(KillWindows.defaults)

    def list_windows(self):
        id = 0
        self.item_to_win = {}

        if self.all_groups:
            windows = [
                w
                for w in self.qtile.windows_map.values()
                if isinstance(w, base.Window)
            ]
        else:
            windows = self.qtile.current_group.windows

        for win in windows:
            if win.group and not isinstance(win.group, ScratchPad):
                item = self.item_format.format(
                    group=win.group.label or win.group.name,
                    id=id,
                    window=win.name,
                )
                self.item_to_win[item] = win
                id += 1

    def run(self):
        self.list_windows()
        self.dmenu_prompt = "Kill selected windows <Ctrk-Ret> to select:"
        self._configure(self.qtile)
        windows = super().run(items=self.item_to_win.keys()).split("\n")

        logger.debug("selected killing window: %s", windows)
        for win in windows:
            win = win.strip()
            if not win:
                continue
            self.dmenu_prompt = "Kill %s" % win
            self._configure(self.qtile)
            if (
                Dmenu.run(self, items=["confirm", "cancel"]).strip()
                == "confirm"
            ):
                try:
                    win = self.item_to_win[win]
                except KeyError:
                    logger.warning("window not found %s", win)
                    # The selected window got closed while the menu was open?
                else:
                    logger.debug("killing window: %s", win)
                    win.kill()


class BringWindowToGroup(WindowList):
    def run(self):
        self.list_windows()
        logger.debug("running summon window")
        items = list(self.item_to_win.keys())
        logger.debug("running summon window %s", items)
        out = super().run()
        logger.debug("running summon window %s", out)

        try:
            sout = out.rstrip("\n")
        except AttributeError:
            # out is not a string (for example it's a Popen object returned
            # by super(WindowList, self).run() when there are no menu items to
            # list
            return

        try:
            win = self.item_to_win[sout]
        except KeyError:
            # The selected window got closed while the menu was open?
            return

        screen = self.qtile.current_screen
        win.togroup(screen.group)
        # screen.set_group(win.group)
        win.group.focus(win)


class History(Dmenu):
    pass


class SessionActions(Dmenu):
    actions = {
        "lock": "gnome-screensaver-command --lock ;;",
        "logout": "loginctl terminate-user %s" % getuser(),
        "shutdown": 'gksu "shutdown -h now" & ;;',
        "restart": check_restart,
        "reboot": 'gksu "shutdown -r now" & ;;',
        "suspend": "gksu pm-suspend && gnome-screensaver-command --lock ;;",
        "hibernate": "gksu pm-hibernate && gnome-screensaver-command --lock ;;",
    }

    def run(self):
        out = super().run(items=self.actions.keys()).strip()
        action  = self.actions[out]
        logger.error("selected: %s:%s", out, action)
        if callable(action):
            action(self.qtile)
        else:
            self.qtile.spawn(action)


class BroTab(Dmenu):
    """
    Give vertical list of all open windows in dmenu. Switch to selected.
    """

    defaults = [
        ("item_format", "* {window}", "the format for the menu items"),
        (
            "all_groups",
            True,
            "If True, list windows from all groups; otherwise only from the current group",
        ),
        ("dmenu_lines", "80", "Give lines vertically. Set to None get inline"),
    ]
    _tabs = None

    def __init__(self, **config):
        Dmenu.__init__(self, **config)
        self.add_defaults(WindowList.defaults)

    def _configure(self, qtile):
        Dmenu._configure(self, qtile)
        self.dbname = "qtile_brotab"

    @property
    def tabs(self):
        if not self._tabs:
            logger.info("initiailizeing tab list")
            self._tabs = [x for x in brotab("list").split("\n") if x]
        return self._tabs

    def run(self):
        # logger.info(self.item_to_win)
        recent = RecentRunner(self.dbname)
        out = super().run(items=self.tabs)
        screen = self.qtile.current_screen

        try:
            sout = out.rstrip("\n")
            bid, title, url = sout.split("\t")
            prefix, windowid, tabid = bid.split(".")
        except AttributeError:
            # out is not a string (for example it's a Popen object returned
            # by super(WindowList, self).run() when there are no menu items to
            # list
            return

        recent.insert(sout)
        brotab(["activate", str(bid)])
        # self.qtile.group["browser"].toscreen()
        self.qtile.toggle_group("browser")


class DmenuRunRecent(DmenuRun):
    defaults = [
        ("dbname", "dbname", "the sqlite db to store history."),
        ("dmenu_command", "dmenu", "the dmenu command to be launched"),
    ]
    qtile = None
    dbname = "qtile_run"
    dmenu_command = "dmenu"

    def __init__(self, **config):
        super().__init__(**config)
        self.add_defaults(super().defaults)

    def _configure(self, qtile):
        self.qtile = qtile
        super()._configure(qtile)

    def run(self):
        logger.error("running %s " % self.__class__.__name__)
        logger.info("running command %s " % self.configured_command)
        recent = RecentRunner(self.dbname)
        selected = (
            super()
            .run(
                items=list(
                    recent.list(
                        list_executables(datetime.utcnow().strftime("%H:%M"))
                    )
                )
            )
            .strip()
        )
        logger.info("Selected: %s", selected)
        if not selected:
            return
        recent.insert(selected)
        # return qtile.spawn(f"systemd-run --user {selected}")
        # return Popen(
        #    ["nohup", selected],
        #    stdout=None,
        #    stdin=None,  # preexec_fn=os.setpgrp
        # )
        return Popen(
            ["systemd-run", "--user"] + selected.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            close_fds=True,
        )


class PassMenu(DmenuRun):
    defaults = [
        ("dbname", "dbname", "the sqlite db to store history."),
        ("dmenu_command", "dmenu", "the dmenu command to be launched"),
    ]
    dmenu_prompt = "pass"
    dbname = "pass_menu"
    dmenu_command = "dmenu"

    def run(self):
        try:
            obs_pause_recording()
            logger.error("running")
            recent = RecentRunner("pass_menu")
            with local.cwd(expanduser("~/.password-store/")):
                passfiles = [
                    splitext(join(base, f))[0][2:]
                    for base, _, files in os.walk(".")
                    for f in files
                    if f.endswith(".gpg")
                ]
            selection = super().run(items=recent.list(passfiles)).strip()
            logger.info("Selected: %s", selection)
            if not selection:
                return
            recent.insert(selection)
            return Popen(
                [
                    join(dirname(__file__), "..", "..", "bin", "passinsert"),
                    selection,
                    str(get_current_window(self.qtile).window.wid),
                ],
                stdout=None,
                stdin=None,
                preexec_fn=os.setpgrp,
            )
        finally:
            obs_resume_recording()


def persist(key, value):
    try:
        rc = get_redis()
        return rc.set(key, value)
    except:
        logger.exception("redis boost failed")


def retreive(key):
    try:
        rc = get_redis()
        return rc.get(key)
    except:
        logger.exception("redis boost failed")


def delete(key):
    try:
        rc = get_redis()
        return rc.delete(key)
    except:
        logger.exception("redis boost failed")


# @hook.subscribe.client_name_updated
def on_inbox_open(client):
    inboxes = get_hostconfig("google_accounts", [])
    for inbox, config in inboxes.items():
        mail_regex = config.get("mail_regex", None)
        if mail_regex and re.match(mail_regex, client.name):
            persist(mail_regex, datetime.now())
            client.to_group("mail")


# @hook.subscribe.client_killed
def on_inbox_close(client):
    inboxes = get_hostconfig("google_accounts", [])
    for inbox, config in inboxes.items():
        mail_regex = config.get("mail_regex", None)
        logger.error("window close %s:%s.", client.name, mail_regex)
        if mail_regex and re.match(mail_regex, client.name):
            delete(mail_regex)


class WindowGroupList(Dmenu):
    """
    Give vertical list of all open windows in dmenu. Switch to selected.
    """

    dmenu_prompt = "WindowGroup"
    recent_runner = None
    dbname = None
    GROUP = "windows"
    item_to_win = {}

    defaults = [
        ("item_format", "* {window}", "the format for the menu items"),
        (
            "all_groups",
            True,
            "If True, list windows from all groups; otherwise only from the current group",
        ),
        ("dmenu_lines", "80", "Give lines vertically. Set to None get inline"),
    ]

    def __init__(self, **config):
        super().__init__(**config)
        self.add_defaults(WindowList.defaults)

    def _configure(self, qtile):
        Dmenu._configure(self, qtile)

    def list_windows(self):
        id = 0
        if self.all_groups:
            windows = self.qtile.windows_map.values()
        else:
            windows = self.qtile.current_group.windows

        for win in windows:
            if win.group:
                item = self.match_item(win)
                self.item_to_win[item] = win
                id += 1

    def run(self, items=None):
        self.list_windows()
        items = [x for x in self.item_to_win.keys()] + [
            x for x in self.recent_runner.list([])
        ]
        out = super().run(items=list(filter(lambda x: x, items)) or [])
        logger.info("WindowGroupList called %s", out)
        screen = self.qtile.current_screen

        try:
            sout = out.strip()
        except AttributeError:
            # out is not a string (for example it's a Popen object returned
            # by super(WindowList, self).run() when there are no menu items to
            # list
            screen.set_group(self.GROUP)
            return
        if not out:
            return

        if not sout.startswith("*"):
            self.recent_runner.insert(sout.split("|", 1)[-1])
        try:
            win = self.item_to_win[sout]
        except KeyError:
            # The selected window got closed while the menu was open?
            return self.spawn(sout)

        if self.qtile.current_group.name != win.group.name:
            screen = self.qtile.current_screen
            screen.set_group(win.group)
        logger.info("WindowGroupList focusing window %s", win)
        win.group.focus(win)
