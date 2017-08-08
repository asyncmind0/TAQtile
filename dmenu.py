import os
from os.path import expanduser, isdir, join, pathsep
from plumbum.cmd import dmenu, emacsclient, bluetoothctl
from recent_runner import RecentRunner
import threading
import re
import time
from screens import SECONDARY_SCREEN, PRIMARY_SCREEN
from libqtile.command import lazy

from log import logger
from dbus_bluetooth import get_devices


def dmenu_show(title, items):
    from themes import dmenu_defaults
    import shlex
    dmenu_defaults = shlex.split(dmenu_defaults)
    logger.info("DMENU: %s", dmenu_defaults)
    try:
        return (dmenu[
            "-i", "-p", "%s " % title
            ] << "\n".join(items))(*dmenu_defaults).strip()
    except Exception as e:
        logger.exception("error running dmenu")


def list_windows(qtile, current_group=False):

    def title_format(x):
        return "%s" % (
            #x.group.name if x.group else '',
            x.name)

    if current_group:
        window_titles = [
            w.name for w in qtile.groupMap[qtile.currentGroup.name].windows
            if w.name != "<no name>"
        ]
    else:
        window_titles = [
            title_format(w) for w in qtile.windowMap.values() if w.name != "<no name>"
        ]
    logger.info(window_titles)

    def process_selected(selected):
        if not current_group:
            group, selected = selected.split(']', 1)
        selected = selected.strip()
        logger.info("Switch to: %s", selected)
        for window in qtile.windowMap.values():
            try:
                if window.group and str(window.name) == str(selected):
                    logger.debug("raise %s:", window)
                    if window.group.screen:
                        qtile.cmd_to_screen(window.group.screen.index)
                    else:
                        window.group.cmd_toscreen()
                    qtile.currentGroup.focus(window, False)
                    return True
            except Exception as e:
                logger.exception("error in group")
        return True

    process_selected(dmenu_show(
        qtile.currentGroup.name if current_group else "*",
        window_titles,
    ))


def list_windows_group(qtile):
    return list_windows(qtile, current_group=True)


def list_executables():
    paths = os.environ["PATH"].split(pathsep)
    executables = []
    for path in filter(isdir, paths):
        for file_ in os.listdir(path):
            if os.access(join(path, file_), os.X_OK):
                executables.append(file_)
    return set(executables)


def dmenu_run(qtile):
    recent = RecentRunner('qtile_run')
    selected = dmenu_show("Run", recent.list(list_executables()))
    print(selected)
    if not selected:
        return
    logger.debug((dir(qtile)))
    qtile.cmd_spawn(selected)
    recent.insert(selected)


def dmenu_org(qtile):
    org_categories = [
        "todo",
        "event",
        "note",
    ]
    title = dmenu_show("Run", org_categories)
    cmd_str = (
        "emacsclient -f xdev -c org-protocol://capture://"
        "url/%s/etext" % (
            title,
        )
    )
    qtile.cmd_spawn(cmd_str)


def list_bluetooth(qtile):
    recent = RecentRunner('qtile_bluetooth')
    devices = get_devices()['/org/bluez/hci0']['devices']
    all_devices = dict([
        (device['Alias'], device['Address'])
        for device in devices.values()
    ])
    selected = dmenu_show("Bluetooth:", recent.list(all_devices.keys()))
    if not selected:
        return
    action = dmenu_show("Action", ["connect", "disconnect"])
    (bluetoothctl << "%s %s\nexit\n" % (action, all_devices[selected]))()
    recent.insert(selected)


def get_window_titles(qtile):
    return [
        w['name'] for w in qtile.cmd_windows()
        if w['name'] != "<no name>"
    ]

def list_calendars(qtile):
    group = 'cal'
    try:
        recent = RecentRunner('qtile_calendar')
        inboxes = {
            'melit.stevenjoseph@gmail.com': "^Google Calendar.*$",
            'steven@stevenjoseph.in': "^stevenjoseph - Calendar.*$",
            'steven@streethawk.co': "Streethawk - Calendar.*$",
        }
        selected = dmenu_show("Calendars:", recent.list(inboxes.keys()))
        if not selected:
            return
        recent.insert(selected)
        match = re.compile(inboxes[selected])
        if qtile.currentScreen.index != PRIMARY_SCREEN:
            logger.debug("cmd_to_screen")
            qtile.cmd_to_screen(PRIMARY_SCREEN)
        if qtile.currentGroup.name != group:
            logger.debug("cmd_toggle_group")
            qtile.currentScreen.cmd_toggle_group(group)
        for window in qtile.cmd_windows():
            if match.match(window['name']):
                logger.debug("Matched" + str(window))
                window = qtile.windowMap.get(window['id'])
                qtile.currentGroup.layout.current = window
                logger.debug("layout.focus")
                qtile.currentGroup.layout.focus(window)
                break
        else:
            cmd = (
                'google-chrome-stable --app="https://calendar.google.com/calendar/b/%s/"' %
                selected
            )

            logger.debug(cmd)
            qtile.cmd_spawn(cmd)

    except:
        logger.exception("error list_calendars")

def list_inboxes(qtile):
    group = 'mail'
    try:
        recent = RecentRunner('qtile_inbox')
        inboxes = [
            'melit.stevenjoseph@gmail.com',
            'steven@stevenjoseph.in',
            'steven@streethawk.co',
            'stevenjose@gmail.com',
        ]
        selected = dmenu_show("Inboxes:", recent.list(inboxes))
        if not selected:
            return
        recent.insert(selected)
        match = re.compile(r"^Inbox .* %s$" % selected)
        if qtile.currentScreen.index != PRIMARY_SCREEN:
            logger.debug("cmd_to_screen")
            qtile.cmd_to_screen(PRIMARY_SCREEN)
        if qtile.currentGroup.name != group:
            logger.debug("cmd_toggle_group")
            qtile.currentScreen.cmd_toggle_group(group)
        for window in qtile.cmd_windows():
            if match.match(window['name']):
                logger.debug("Matched" + str(window))
                window = qtile.windowMap.get(window['id'])
                qtile.currentGroup.layout.current = window
                logger.debug("layout.focus")
                qtile.currentGroup.layout.focus(window)
                break
        else:
            cmd = (
                'google-chrome-stable --app="https://inbox.google.com/u/%s/"' %
                selected
            )

            logger.debug(cmd)
            qtile.cmd_spawn(cmd)

    except:
        logger.exception("error list_inboxes")


def dmenu_clip(qtile):
    try:
        recent = RecentRunner('qtile_clip')
        selected = dmenu_show("Clip:", recent.recent())
        #logger.debug("CLIP selected %s" % selected)
        #logger.debug("env  %s" % os.environ['XAUTHORITY'])
        #import clipboard
        #clipboard.copy(selected)

        try:
            from Tkinter import Tk
        except ImportError:
            from tkinter import Tk
        r = Tk()
        r.withdraw()
        r.clipboard_clear()
        r.clipboard_append(selected)
        r.update() # now it stays on the clipboard after the window is closed
        r.destroy()
    except Exception as e:
        logger.exception("error in clip access")
