import os
from datetime import datetime
import re
from os.path import dirname, join, splitext, expanduser, isdir, pathsep
from subprocess import Popen

from libqtile.extension.dmenu import Dmenu, DmenuRun
from libqtile.extension.window_list import WindowList
from libqtile import hook

from plumbum import local

from log import logger
from recent_runner import RecentRunner
from system import (
    get_current_window,
    get_hostconfig,
    window_exists,
    get_windows_map,
    get_current_screen,
    get_current_group,
)
from system import get_redis
from functools import lru_cache


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
        win.cmd_togroup(screen.group)
        # screen.set_group(win.group)
        win.group.focus(win)


class Surf(Dmenu):
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

    def __init__(self, **config):
        super().__init__(**config)
        self.add_defaults(WindowList.defaults)

    def _configure(self, qtile):
        Dmenu._configure(self, qtile)
        self.dbname = "qtile_surf"

    def list_windows(self):
        id = 0
        self.item_to_win = {}

        if self.all_groups:
            windows = self.qtile.windows_map.values()
        else:
            windows = self.qtile.current_group.windows

        for win in windows:
            if win.group:
                # logger.info(dir(win.window))
                if win.window.get_wm_class()[0] != "surf":
                    continue
                item = self.item_format.format(
                    group=win.group.label or win.group.name,
                    id=id,
                    window=win.name,
                )
                self.item_to_win[item] = win
                id += 1

    def run(self):
        self.list_windows()
        # logger.info(self.item_to_win)
        recent = RecentRunner(self.dbname)
        out = super().run(
            items=(
                [x for x in self.item_to_win.keys()]
                + [x for x in recent.list([])]
            )
        )
        screen = self.qtile.current_screen

        try:
            sout = out.rstrip("\n")
        except AttributeError:
            # out is not a string (for example it's a Popen object returned
            # by super(WindowList, self).run() when there are no menu items to
            # list
            screen.set_group("surf")
            return

        recent.insert(sout[2:] if sout.startswith("*") else sout)
        try:
            win = self.item_to_win[sout]
        except KeyError:
            # The selected window got closed while the menu was open?
            if sout.startswith("http"):
                self.qtile.cmd_spawn("surf %s" % sout.strip())
            elif sout:
                self.qtile.cmd_spawn(
                    "surf https://www.google.com/search?q='%s'&ie=utf-8&oe=utf-8"
                    % sout
                )
            return

        screen.set_group(win.group)
        win.group.focus(win)
        logger.info(
            win.window.get_property("_SURF_URI", "STRING").value.to_string()
        )


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
        self.qtile.cmd_toggle_group("browser")


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
        logger.error("running %s" % self.__class__.__name__)
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
        return Popen(
            ["nohup", selected], stdout=None, stdin=None, preexec_fn=os.setpgrp
        )


class PassMenu(DmenuRun):
    defaults = [
        ("dbname", "dbname", "the sqlite db to store history."),
        ("dmenu_command", "dmenu", "the dmenu command to be launched"),
    ]
    qtile = None
    dbname = "pass_menu"
    dmenu_command = "dmenu"

    def __init__(self, **config):
        super().__init__(**config)
        self.add_defaults(super().defaults)

    def _configure(self, qtile):
        self.qtile = qtile
        super()._configure(qtile)

    def run(self):
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
                join(dirname(__file__), "bin", "passinsert"),
                selection,
                str(get_current_window(self.qtile).window.wid),
            ],
            stdout=None,
            stdin=None,
            preexec_fn=os.setpgrp,
        )


class Inboxes(DmenuRun):
    defaults = [
        ("dbname", "list_inboxes", "the sqlite db to store history."),
        ("dmenu_command", "dmenu", "the dmenu command to be launched"),
        ("group", "mail", "the group to use."),
    ]

    def __init__(self, **config):
        super().__init__(**config)
        self.add_defaults(Inboxes.defaults)
        self.launched = {}

    def run(self):
        recent = RecentRunner(self.dbname)
        inboxes = get_hostconfig("google_accounts", [])
        qtile = self.qtile
        group = self.group
        if get_current_group(qtile).name != group:
            logger.debug("cmd_toggle_group")
            get_current_screen(qtile).cmd_toggle_group(group)
        selected = super().run(items=recent.list(inboxes)).strip()
        logger.info("Selected: %s", selected)
        if not selected or selected not in inboxes:
            recent.remove(selected)
            return
        recent.insert(selected)
        mail_regex = inboxes[selected].get("mail_regex", ".*%s.*" % selected)
        # mail_regex = ".*%s.*" % selected
        window = window_exists(qtile, re.compile(mail_regex, re.I))
        logger.debug("mail window exists %s regex %s ", window, mail_regex)
        # rc = get_redis()
        # is_launched = rc.get(mail_regex)
        if window:
            # window = get_windows_map(qtile).get(window.window.wid)
            logger.debug("Matched %s", str(window))
            window.cmd_togroup(group)
            logger.debug("layout.focus")
            get_current_group(qtile).focus(window)
        else:
            cmd = (
                # "google-chrome-stable",
                "/usr/sbin//systemd-run",
                "--user",
                "--slice=browser.slice",
                "brave",
                "--app=https://mail.google.com/mail/u/%s/#inbox" % selected,
                "--profile-directory=%s" % inboxes[selected]["profile"],
            )

            logger.info(cmd)
            qtile.cmd_spawn(cmd)
            # rc.set(mail_regex, datetime.now().timestamp())
            # return Popen(cmd, stdout=None, stdin=None, preexec_fn=os.setpgrp)


@hook.subscribe.client_name_updated
def on_inbox_open(client):
    inboxes = get_hostconfig("google_accounts", [])
    for inbox, config in inboxes.items():
        mail_regex = config.get("mail_regex", None)
        if mail_regex and re.match(mail_regex, client.name):
            rc = get_redis()
            rc.set(mail_regex, datetime.now())
            client.to_group("mail")


@hook.subscribe.client_killed
def on_inbox_close(client):
    inboxes = get_hostconfig("google_accounts", [])
    for inbox, config in inboxes.items():
        mail_regex = config.get("mail_regex", None)
        logger.error("window close %s:%s.", client.name, mail_regex)
        if mail_regex and re.match(mail_regex, client.name):
            rc = get_redis()
            rc.delete(mail_regex)
