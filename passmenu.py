from __future__ import print_function

import logging
import os

log = logging.getLogger("qtile")


def passmenu(qtile, args):
    from plumbum import local
    try:
        dmenu = local['dmenu']
        xdotool = local['xdotool']
        envoyexec = local['envoy-exec']

        with local.cwd(os.path.expanduser("~/.password-store/")):
            passfiles = [
                os.path.splitext(os.path.join(base, f))[0][2:]
                for base, _, files in os.walk('.')
                for f in files if f.endswith(".gpg")
            ]

        args = args.split(' ')
        args.extend(['-p', 'Pass:'])

        selection = (dmenu[args] << '\n'.join(reversed(passfiles)))(
            retcode=None)
        xdotool(
            'type', '--clearmodifiers',
            envoyexec('pass', 'show', selection.strip()).split('\n')[0].strip())
    except:
        logging.exception("Error getting pass")
