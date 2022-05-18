import os
import re
from datetime import datetime
from functools import lru_cache
from getpass import getuser
from os.path import dirname, join, splitext, expanduser, isdir, pathsep
from subprocess import Popen
from urllib.parse import quote_plus

from libqtile import hook
from libqtile.extension.dmenu import Dmenu, DmenuRun
from libqtile.extension.window_list import WindowList
from plumbum import local

from taqtile.log import logger
from taqtile.recent_runner import RecentRunner
from taqtile.system import (
    get_current_window,
    get_hostconfig,
    window_exists,
    get_current_screen,
    get_current_group,
    get_redis,
)

SURF_HISTORY_DB = "qtile_surf"
surf_recent_runner = RecentRunner(SURF_HISTORY_DB)


@hook.subscribe.client_name_updated
def save_history(client):
    uri = None
    logger.debug("name updated  %s", client)
    try:
        uri = client.window.get_property(
            "_SURF_URI", "UTF8_STRING"
        ).value.to_utf8()
        logger.info(uri)
        surf_recent_runner.insert(uri)

    except AttributeError:
        logger.exception("failed to get uri updated ")


class Surf(Dmenu):
    """
    Give vertical list of all open windows in dmenu. Switch to selected.
    """

    dmenu_prompt = "Surf"
    recent_runner = None
    dbname = SURF_HISTORY_DB

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
        self.recent_runner = surf_recent_runner
        self.item_to_win = {}

    def _configure(self, qtile):
        Dmenu._configure(self, qtile)

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
                    window=win.name.split("|", 1)[-1],
                )
                self.item_to_win[item] = win
                id += 1

    def run(self, items=None):
        self.list_windows()
        items = [x for x in self.item_to_win.keys()] + [
            x for x in self.recent_runner.list([])
        ]
        out = super().run(items=items)
        logger.info("surf called %s", out)
        screen = self.qtile.current_screen

        try:
            sout = out.rstrip("\n")
        except AttributeError:
            # out is not a string (for example it's a Popen object returned
            # by super(WindowList, self).run() when there are no menu items to
            # list
            screen.set_group("surf")
            return

        if not sout.startswith("*"):
            self.recent_runner.insert(sout.split("|", 1)[-1])
        try:
            win = self.item_to_win[sout]
        except KeyError:
            # The selected window got closed while the menu was open?
            if sout.startswith("http"):
                self.qtile.cmd_spawn(
                    # "/usr/sbin//systemd-run --user --slice=browser.slice /usr/local/bin/surf %s"
                    "surf %s"
                    % sout.strip()
                )
            elif sout:
                gg = "gg "
                if sout.startswith(gg):
                    sout = sout.split(gg)[-1]
                    cmd = "surf https://www.google.com/search?q='%s'&ie=utf-8&oe=utf-8"
                else:
                    cmd = "surf https://duckduckgo.com/?t=ffab&q=%s&ia=web"
                self.qtile.cmd_spawn(cmd % quote_plus(sout))
            return

        if self.qtile.current_group.name != win.group.name:
            screen = self.qtile.current_screen
            screen.set_group(win.group)
        logger.info("surf focusing window %s", win)
        win.group.focus(win)
