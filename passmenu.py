from __future__ import print_function

import logging
import os
from dmenu import dmenu_show
from recent_runner import RecentRunner

MAX_PASS = 200
log = logging.getLogger("qtile")


def passmenu(qtile, args):
    recent = RecentRunner('pass_menu')
    from plumbum import local, ProcessExecutionError
    try:
        xdotool = local['xdotool']
        envoyexec = local['envoy-exec']
        notify_send = local['notify-send']

        with local.cwd(os.path.expanduser("~/.password-store/")):
            passfiles = [
                os.path.splitext(os.path.join(base, f))[0][2:]
                for base, _, files in os.walk('.')
                for f in files if f.endswith(".gpg")
            ]

        args = args.split(' ')
        args.extend(['-p', 'Pass:'])
        log.error(passfiles)

        selection = dmenu_show("pass", recent.list(passfiles))
        if not selection:
            return
        password = None
        with local.env(DISPLAY=''):
            try:
                password = envoyexec(
                    'pass', 'show',
                    selection,
                    timeout=5,
                )
            except ProcessExecutionError as e:
                logging.exception("Error getting pass output")
                notify_send("-u", "critical", "GPG is locked ?")
        password = password.strip()
        if not password:
            return
        if len(password) > MAX_PASS:
            notify_send("-u", "critical", "Pass out put larger than %s, skipping." % MAX_PASS)
            return
        xdotool(
            'type', '--clearmodifiers',
            password)
        recent.insert(selection)
    except:
        logging.exception("Error getting pass")
