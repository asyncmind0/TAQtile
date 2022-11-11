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
from taqtile.extensions.base import WindowGroupList

SURF_HISTORY_DB = "qtile_surf"
surf_recent_runner = RecentRunner(SURF_HISTORY_DB)


@hook.subscribe.client_name_updated
def save_history(client):
    uri = None
    try:
        uri = getattr(
            client.window.get_property("_SURF_URI", "UTF8_STRING"),
            "value",
            None,
        )
        if uri:
            uri = uri.to_utf8()
            logger.info(uri)
            # surf_recent_runner.insert(uri)

    except AttributeError:
        logger.exception("failed to get uri updated ")


class Surf(WindowGroupList):
    """
    Give vertical list of all open windows in dmenu. Switch to selected.
    """

    dmenu_prompt = "Surf"
    recent_runner = surf_recent_runner
    dbname = SURF_HISTORY_DB
    GROUP = "surf"

    defaults = [
        ("item_format", "* {window}", "the format for the menu items"),
        (
            "all_groups",
            True,
            "If True, list windows from all groups; otherwise only from the current group",
        ),
        ("dmenu_lines", "80", "Give lines vertically. Set to None get inline"),
    ]

    def match_item(self, win):
        # logger.info(dir(win.window))
        if win.window.get_wm_class()[0] != "surf":
            return
        return self.item_format.format(
            group=win.group.label or win.group.name,
            id=id,
            window=win.name.split("|", 1)[-1],
        )

    def spawn(self, sout):
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


class Calendars(WindowGroupList):

    dmenu_prompt = "Calendars"
    recent_runner = None
    dbname = "calendars"
    GROUP = "cal"
