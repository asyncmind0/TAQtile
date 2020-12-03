import os
import re
import shlex
from os.path import isdir, join, pathsep, dirname

from plumbum.cmd import dmenu, bluetoothctl, clipmenu, xdotool, pacmd

from log import logger
from recent_runner import RecentRunner
from screens import PRIMARY_SCREEN, SECONDARY_SCREEN
from dbus_bluetooth import get_devices
from themes import dmenu_cmd_args
from system import get_hostconfig, window_exists, get_windows_map, get_current_screen, get_current_group


def dmenu_show(title, items):
    items = list(items)
    dmenu_args = shlex.split(dmenu_cmd_args(dmenu_lines=min(30, len(items))))
    logger.info("DMENU: %s", dmenu_args)
    try:
        return (
            dmenu[
                     "-c", "-i", "-p", "%s " % title
            ] << "\n".join(items))(*dmenu_args).strip()
    except Exception as e:
        logger.exception("error running dmenu")


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
    action = dmenu_show("Action", ["connect", "disconnect", "music", "voice"])
    if action in ["music", "voice"]:
        logger.info(
                "bluez_card.%s", all_devices[selected].replace(':', '_'),
            )
        logger.info(
            pacmd(
                "set-card-profile",
                "bluez_card.%s" % all_devices[selected].replace(':', '_'),
                {"music": "a2dp_sink_aptx", "voice": "headset_head_unit"}[action]
            )
        )
    else:
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
        inboxes = get_hostconfig('google_accounts', [])
        selected = dmenu_show("Calendars:", recent.list(inboxes.keys()))
        if not selected or selected not in inboxes.keys():
            return
        recent.insert(selected)
        match = re.compile(inboxes[selected]['calendar_regex'], re.I)
        if get_current_screen(qtile).index != SECONDARY_SCREEN:
            logger.debug("cmd_to_screen")
            qtile.cmd_to_screen(SECONDARY_SCREEN)
        if get_current_group(qtile).name != group:
            logger.debug("cmd_toggle_group")
            get_current_screen(qtile).cmd_toggle_group(group)
        for window in qtile.cmd_windows():
            if match.match(window['name']):
                logger.debug("Matched %s", str(window))
                window = get_windows_map(qtile).get(window['id'])
                get_current_group(qtile).layout.current = window
                logger.debug("layout.focus")
                get_current_group(qtile).layout.focus(window)
                break
        else:
            cmd = (
                #'chromium --app="https://calendar.google.com/calendar/b/%s/" --profile-directory=%s' %
                'firefox --new-window  --kiosk "https://calendar.google.com/calendar/b/%s/"  -P %s' % 
                (
                    selected,
                    inboxes[selected]['profile'],
                )
            )

            logger.debug(cmd)
            qtile.cmd_spawn(cmd)

    except:
        logger.exception("error list_calendars")

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


def dmenu_pushbullet(qtile):
    pushbullet_api_key = get_hostconfig('pushbullet_api_key', [])
    from pushbullet import PushBullet
    pb = PushBullet(pushbullet_api_key)
    device = dmenu_show("Devices:", [x.nickname for x in pb.devices])
    device = pb.get_device(device)
    title = "Select clip item to push: "
    dmenu_args = shlex.split(dmenu_cmd_args(dmenu_lines=min(30, len(items))))
    body = clipmenu[
            "-i", "-p", "%s" % title
        ](*dmenu_args).strip()
    device.push_note(
        "Shared from %s" % socket.gethostname(),
        open(body).read()
        
    )
