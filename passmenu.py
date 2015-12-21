from __future__ import print_function

import logging
import os

MAX_PASS = 200
log = logging.getLogger("qtile")


def passmenu(qtile, args):
    from plumbum import local, ProcessExecutionError
    try:
        dmenu = local['dmenu']
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

        selection = (dmenu[args] << '\n'.join(reversed(passfiles)))(
            retcode=None).strip()
        if not selection:
            return
        password = None
        try:
            password = envoyexec('pass', 'show', selection)
        except ProcessExecutionError as e:
            logging.exception("Error getting pass output")
            notify_send(str(e))
        password = password.strip()
        if not password:
            return
        if len(password) > MAX_PASS:
            notify_send("Pass out put larger than %s, skipping." % MAX_PASS)
            return
        xdotool(
            'type', '--clearmodifiers',
            password)
    except:
        logging.exception("Error getting pass")
