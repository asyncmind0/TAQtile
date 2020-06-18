import os
import re
import shlex
from os.path import isdir, join, pathsep, dirname

from plumbum.cmd import dmenu, bluetoothctl, clipmenu, xdotool, rofi

from log import logger
from recent_runner import RecentRunner
from screens import PRIMARY_SCREEN, SECONDARY_SCREEN
from dbus_bluetooth import get_devices
from themes import dmenu_defaults
from system import get_hostconfig, window_exists, get_windows_map, get_current_screen, get_current_group


def dmenu_show(title, items):
    dmenu_args = shlex.split(dmenu_defaults())
    logger.info("DMENU: %s", dmenu_args)
    try:
        return (
            dmenu[
           # rofi[
            #"-dmenu",
                     "-i", "-p", "%s " % title
            ] << "\n".join(items))(*dmenu_args).strip()
    except Exception as e:
        logger.exception("error running dmenu")


def list_windows(qtile, current_group=False):

    def title_format(x):
        return "%s" % (
            #x.group.name if x.group else '',
            x.name)

    if current_group:
        window_titles = [
            w.name for w in qtile.group_map[get_current_group(qtile).name].windows
            if w.name != "<no name>"
        ]
    else:
        window_titles = [
            title_format(w) for w in get_windows_map(qtile).values() if w.name != "<no name>"
        ]
    logger.info(window_titles)

    def process_selected(selected):
        if not current_group:
            group, selected = selected.split(']', 1)
        selected = selected.strip()
        logger.info("Switch to: %s", selected)
        for window in get_windows_map(qtile).values():
            try:
                if window.group and str(window.name.decode('utf8')) == str(selected):
                    logger.debug("raise %s:", window)
                    if window.group.screen:
                        qtile.cmd_to_screen(window.group.screen.index)
                    else:
                        window.group.cmd_toscreen()
                    get_current_group(qtile).focus(window, False)
                    return True
            except Exception as e:
                logger.exception("error in group")
        return True

    process_selected(dmenu_show(
        get_current_group(qtile).name if current_group else "*",
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
    all_devices = {
        device['Alias']: device['Address']
        for device in devices.values()
    }
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
        if not selected or selected not in inboxes.keys():
            return
        recent.insert(selected)
        match = re.compile(inboxes[selected], re.I)
        if get_current_screen(qtile).index != SECONDARY_SCREEN:
            logger.debug("cmd_to_screen")
            qtile.cmd_to_screen(SECONDARY_SCREEN)
        if get_current_group(qtile).name != group:
            logger.debug("cmd_toggle_group")
            get_current_screen(qtile).cmd_toggle_group(group)
        for window in qtile.cmd_windows():
            if match.match(window['name']):
                logger.debug("Matched %%", str(window))
                window = get_windows_map(qtile).get(window['id'])
                get_current_group(qtile).layout.current = window
                logger.debug("layout.focus")
                get_current_group(qtile).layout.focus(window)
                break
        else:
            cmd = (
                'chromium --app="https://calendar.google.com/calendar/b/%s/"' %
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
        inboxes = get_hostconfig('google_accounts', [])
        selected = dmenu_show("Inboxes:", recent.list(inboxes))
        if not selected or selected not in inboxes:
            return
        recent.insert(selected)
        if get_current_screen(qtile).index != SECONDARY_SCREEN:
            logger.debug("cmd_to_screen")
            qtile.cmd_to_screen(SECONDARY_SCREEN)
        if get_current_group(qtile).name != group:
            logger.debug("cmd_toggle_group")
            get_current_screen(qtile).cmd_toggle_group(group)
        window = window_exists(qtile, re.compile(r"mail.google.com__mail_u_%s" % selected, re.I))
        if window:
            window = get_windows_map(qtile).get(window.window.wid)
            logger.debug("Matched %s", str(window))
            window.cmd_togroup(group)
            logger.debug("layout.focus")
            get_current_group(qtile).focus(window)
        else:
            cmd = (
                'chromium --app="https://mail.google.com/mail/u/%s/#inbox"' %
                selected
            )

            logger.debug(cmd)
            qtile.cmd_spawn(cmd)

    except:
        logger.exception("error list_inboxes")


def dmenu_web(qtile):
    group = 'monit'
    try:
        recent = RecentRunner('qtile_web')
        selected = dmenu_show("links:", recent.list([]))
        if not selected:
            return
        recent.insert(selected)
        if get_current_screen(qtile).index != SECONDARY_SCREEN:
            logger.debug("cmd_to_screen")
            qtile.cmd_to_screen(SECONDARY_SCREEN)
        if get_current_group(qtile).name != group:
            logger.debug("cmd_toggle_group")
            get_current_screen(qtile).cmd_toggle_group(group)
        window = window_exists(qtile, re.compile(r"mail.google.com__mail_u_%s" % selected, re.I))
        if window:
            window = get_windows_map(qtile).get(window.window.wid)
            logger.debug("Matched" + str(window))
            window.cmd_togroup(group)
            logger.debug("layout.focus")
            get_current_group(qtile).focus(window)
        else:
            cmd = (
                'chromium --app="https://mail.google.com/mail/u/%s/#inbox"' %
                selected
            )

            logger.debug(cmd)
            qtile.cmd_spawn(cmd)
    except:
        logger.exception("error list_inboxes")

def dmenu_clip(qtile):
    title = "Clipboard: "
    dmenu_args = shlex.split(dmenu_defaults())
    logger.info("DMENU: %s", dmenu_args)
    try:
        xdotool(
            "type",
            "--clearmodifiers",
            "--",
            clipmenu[
                "-i", "-p", "%s" % title
            ](*dmenu_args).strip()
        )
    except Exception as e:
        logger.exception("error in clip access")
