from __future__ import print_function

import logging
import os

from plumbum import local


log = logging.getLogger("qtile")


def passmenu(qtile, args):
    try:
        dmenu = local['dmenu']
        echo = local['echo']
        xdotool = local['xdotool']
        pass_ = local['pass']

        with local.cwd(os.path.expanduser("~/.password-store/")):
            passfiles = [
                os.path.splitext(os.path.join(base, f))[0][2:]
                for base, _, files in os.walk('.')
                for f in files if f.endswith(".gpg")
            ]

        args = args.split(' ')
        args.extend(['-p', 'Pass:'])

        selection = (echo['\n'.join(reversed(passfiles))] | dmenu[args])(
            retcode=None)
        xdotool(
            'type', '--clearmodifiers',
            pass_('show', selection.strip()).split('\n')[0].strip())
    except:
        logging.exception("Error getting pass")
