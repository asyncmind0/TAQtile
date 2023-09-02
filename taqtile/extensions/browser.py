import os
import re
from datetime import datetime
from functools import lru_cache
from getpass import getuser
from os.path import dirname, join, splitext, expanduser, isdir, pathsep
from subprocess import Popen
from urllib.parse import quote_plus

from libqtile import hook
from libqtile.extension.window_list import WindowList
from plumbum import local

from taqtile.recent_runner import RecentRunner
from libqtile.extension.dmenu import Dmenu, DmenuRun
from taqtile.system import (
    get_current_window,
    get_hostconfig,
    window_exists,
    get_current_screen,
    get_current_group,
    get_redis,
    group_by_name
)
import logging

logger = logging.getLogger("taqtile")


class BrowserAppLauncher(DmenuRun):
    config_key = "browser_accounts"

    def __init__(self, **config):
        super().__init__(**config)
        self.add_defaults(self.defaults)
        self.accounts = get_hostconfig("browser_accounts", [])

    def handle_selected_item(self, selected, regex, logger) -> None:
        qtile = self.qtile
        group = self.group
        if not selected or selected not in self.accounts:
            self.recent.remove(selected)
            return
        self.recent.insert(selected)
        if get_current_group(qtile).name != group:
            group = group_by_name(qtile.groups, group)
            get_current_screen(qtile).toggle_group(group)
        logger.debug("Does Window exists with regex %s", regex)
        window = window_exists(self.qtile, re.compile(regex, re.I))
        logger.debug("Window exists with regex %s: %s", regex, window)
        if window:
            window.togroup(self.group)
            get_current_group(self.qtile).focus(window)
        else:
            cmd = " ".join(
                [
                    "browser.py",
                    "--use-default",
                    f"--profile=%s"
                    % self.accounts[selected]["profile"].lower(),
                    self.url_template % selected,
                ]
            )

            logger.info("Command: %s", cmd)
            return qtile.cmd_spawn(cmd)

    def run(self):
        self.recent = RecentRunner(self.dbname)
        logger.info(f"Accounts: {self.accounts}")
        selected = super().run(items=self.recent.list(self.accounts)).strip()
        logger.info(f"Selected: {selected}")
        self.handle_selected_item(
            selected,
            (
                self.accounts[selected]
                .get(self.config_key, {"regex": ".*%s.*" % selected})
                .get("regex")
            ),
            logger,
        )


class Inboxes(BrowserAppLauncher):
    defaults = [
        ("dbname", "list_inboxes", "The SQLite database to store the history."),
        ("dmenu_command", "dmenu", "The dmenu command to be launched."),
    ]
    config_key = "mail"
    group = "mail"
    url_template = "https://mail.google.com/mail/u/%s/#inbox"


class Calendars(BrowserAppLauncher):
    defaults = [
        (
            "dbname",
            "list_calendars",
            "The SQLite database to store the history.",
        ),
        ("dmenu_command", "dmenu", "The dmenu command to be launched."),
    ]
    config_key = "calendar"
    group = "calendar"
    url_template = "https://calendar.google.com/calendar/b/%s/"
