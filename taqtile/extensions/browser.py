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

PROFILES = {"home": {}, "work": {}}


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
        inboxes = get_hostconfig("browser_accounts", [])
        qtile = self.qtile
        group = self.group
        if get_current_group(qtile).name != group:
            logger.debug("cmd_toggle_group")
            get_current_screen(qtile).toggle_group(group)
        selected = super().run(items=recent.list(inboxes)).strip()
        logger.info(f"Selected: {selected}, Inboxes {inboxes}")
        if not selected or selected not in inboxes:
            recent.remove(selected)
            return
        recent.insert(selected)
        mail_regex = inboxes[selected].get("mail_regex", ".*%s.*" % selected)
        # mail_regex = ".*%s.*" % selected
        window = window_exists(qtile, re.compile(mail_regex, re.I))
        logger.debug("mail window exists %s regex %s ", window, mail_regex)
        if window:
            # window = get_windows_map(qtile).get(window.window.wid)
            logger.debug("Matched %s", str(window))
            window.togroup(group)
            logger.debug("layout.focus")
            get_current_group(qtile).focus(window)
        else:
            cmd = (
                # "google-chrome-stable",
                # "/usr/sbin//systemd-run",
                # "--user",
                # "--slice=browser.slice",
                "/usr/sbin/chromium",
                # "-u",
                # "Firefox/99.0",
                # "https://mail.google.com/mail/u/%s/#inbox" % selected,
                # "--class=email",
                "--app=https://mail.google.com/mail/u/%s/#inbox" % selected,
                "--user-data-dir=/home/steven/.config/chromium.%s"
                % inboxes[selected]["profile"].lower(),
            )

            logger.info(cmd)
            qtile.spawn(cmd)
            # rc.set(mail_regex, datetime.now().timestamp())
            # return Popen(cmd, stdout=None, stdin=None, preexec_fn=os.setpgrp)


class Calendars(DmenuRun):
    defaults = [
        ("dbname", "list_calendars", "the sqlite db to store history."),
        ("dmenu_command", "dmenu", "the dmenu command to be launched"),
        ("group", "cal", "the group to use."),
    ]

    def __init__(self, **config):
        super().__init__(**config)
        self.add_defaults(Calendars.defaults)
        self.launched = {}

    def run(self):
        recent = RecentRunner(self.dbname)
        calendars = get_hostconfig("browser_accounts", [])
        qtile = self.qtile
        group = self.group
        if get_current_group(qtile).name != group:
            logger.debug("cmd_toggle_group")
            get_current_screen(qtile).toggle_group(group)
        selected = super().run(items=recent.list(calendars)).strip()
        logger.info(f"Selected: {selected}, Calendars {calendars}")
        if not selected or selected not in calendars:
            recent.remove(selected)
            return
        recent.insert(selected)
        regex = calendars[selected].get("calendar_regex", ".*%s.*" % selected)
        window = window_exists(qtile, re.compile(regex, re.I))
        logger.debug("calendar window exists %s regex %s ", window, regex)
        if window:
            # window = get_windows_map(qtile).get(window.window.wid)
            logger.debug("Matched %s", str(window))
            window.togroup(group)
            logger.debug("layout.focus")
            get_current_group(qtile).focus(window)
        else:
            cmd = (
                # "google-chrome-stable",
                # "/usr/sbin//systemd-run",
                # "--user",
                # "--slice=browser.slice",
                "/usr/sbin/brave",
                # "-u",
                # "Firefox/99.0",
                # "https://mail.google.com/mail/u/%s/#inbox" % selected,
                "--app=https://calendar.google.com/calendar/b/%s/" % selected,
                "--profile-directory=%s" % calendars[selected]["profile"],
            )

            logger.info("calendar command: %s", cmd)
            qtile.spawn(cmd)
