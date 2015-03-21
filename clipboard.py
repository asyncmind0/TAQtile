from __future__ import print_function
import logging
import os
from libqtile import hook, xcbq
import json
from plumbum import local

log = logging.getLogger("qtile")
use_selection = 'CLIPBOARD'
blacklist = []
blacklist_text = "*********"
history_len = 50
previous_clip = None
count_call = 0
history_file = os.path.expanduser("~/.qtile-cliphistory")


def is_blacklisted(owner_id):
    if not blacklist:
        return False

    if owner_id in hook.qtile.windowMap:
        owner = hook.qtile.windowMap[owner_id].window
    else:
        owner = xcbq.Window(hook.qtile.conn, owner_id)

    owner_class = owner.get_wm_class()
    if owner_class:
        for wm_class in blacklist:
            if wm_class in owner_class:
                return True


@hook.subscribe.selection_change
def hook_change(name, selection):
    global previous_clip
    global count_call
    if name != use_selection:
        return

    if selection['selection'] == previous_clip:
        return

    if is_blacklisted(selection["owner"]):
        text = blacklist_text
    else:
        text = selection["selection"].replace("\n", " ")
        text = text.strip()
    if not text:
        return

    count_call += 1
    previous_clip = text
    log.error("CLIPBOARD %s" % text)
    log.error("count_call %s" % count_call)
    history = []
    if os.path.isfile(history_file):
        with open(history_file, 'r') as qfile:
            history = json.load(qfile)
    if text in history:
        history.remove(text)
    history.append(text)
    with open(history_file, 'w+') as qfile:
        json.dump(history, qfile)


def dmenu_xclip(qtile, args):
    dmenu = local['dmenu']
    echo = local['echo']
    xclip = local['xclip']

    logging.basicConfig(level=logging.DEBUG)
    history = []
    args = args.split(' ')
    args.extend(['-p', 'Clip:'])

    if os.path.isfile(history_file):
        with open(history_file, 'r') as qfile:
            history = json.load(qfile)

    command = (echo['\n'.join(reversed(history))] | dmenu[args])(retcode=None)
    outf = os.popen('xclip -selection secondary', 'w')
    outf.write(command)
    outf.close()
    outf = os.popen('xclip -selection primary', 'w')
    outf.write(command)
    outf.close()
    #(echo[command] | xclip['-i', '-selection', 'primary'])()
    #(echo[command] | xclip['-i', '-selection', 'secondary'])()
