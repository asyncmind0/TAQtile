from __future__ import print_function

import os
from os.path import dirname, join
from dmenu import dmenu_show
from recent_runner import RecentRunner
from libqtile.log_utils import logger as log
from plumbum import local
from time import sleep

MAX_PASS = 200


def passmenu(qtile, args):
    try:
        recent = RecentRunner('pass_menu')
        with local.cwd(os.path.expanduser("~/.password-store/")):
            passfiles = [
                os.path.splitext(os.path.join(base, f))[0][2:]
                for base, _, files in os.walk('.')
                for f in files if f.endswith(".gpg")
            ]
        args = args.split(' ')
        args.extend(['-p', 'Pass:'])
        selection = dmenu_show("pass", recent.list(passfiles))
        if not selection:
            return
        qtile.cmd_spawn(
            [
                join(dirname(__file__), "bin", "passinsert"),
                selection,
                str(qtile.currentWindow.window.wid),
            ]
        )
        recent.insert(selection)
    except:
        log.exception("Error getting pass")
