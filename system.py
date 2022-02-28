"""Platform specific configurtation options
"""
import glob
import logging
import os
import platform
import re
import signal
import subprocess
from functools import lru_cache
from os.path import expanduser

from plumbum import local

from log import logger


passstore = local["pass"]

# TODO https://confuse.readthedocs.io/en/latest/

mod = "mod4"

common_autostart = {
    "xcompmgr": None,
    expanduser("~/.bin/xstartup"): None,
    "setxkbmap -option 'ctrl:swapcaps'": None,
    # "surf 'https://grafana-bison.streethawk.com/d/000000005/bison-riak?refresh=15m'": None,
    # "surf 'https://grafana-bison.streethawk.com/d/000000003/bison-rabbitmq?orgId=1&from=now-1h&to=now&refresh=5m'": None,
    # "surf 'https://grafana.streethawk.com/d/000000004/bison-load?orgId=1&from=now-1h&to=now&refresh=15m'": None,
    "dropbox": None,
}

laptop_autostart = dict(common_autostart)
laptop_autostart.update(
    {
        #'blueman-applet': None,
        "insync start": None,
        #'parcellite': None,
        "slack": None,
        "feh --bg-scale ~/.wallpaper": None,
        #'discord': None,
        "whatsapp-web-desktop": dict(
            process_filter="whatsapp",
            window_regex=re.compile(r".*whatsapp.*", re.I),
        ),
    }
)

desktop_autostart = dict(common_autostart)
desktop_autostart.update({"jabberel-tray.py": None})
default_config = {
    "screens": {
        0: 2,
        1: 1,
        2: 0,
        3: 3,
    },
    "term0_key": "F11",
    "term1_key": "F12",
    "term2_key": "XF86Launch5",
    "term3_key": "F9",
    "google_accounts": {
        "melit.stevenjoseph@gmail.com": {
            "calendar_regex": r"^Google Calendar.*$",
            "mail_regex": r".*melit\.stevenjoseph@gmail\.com.*$",
            # "profile": "default-release",
            "profile": "Home",
        },
        "steven@stevenjoseph.in": {
            "calendar_regex": r"^stevenjoseph - Calendar.*$",
            "mail_regex": r".*steven@stevenjoseph.*$",
            # "profile": "default-release",
            "profile": "Home",
        },
        "steven@streethawk.co": {
            "calendar_regex": r"Streethawk - Calendar.*$",
            "mail_regex": r".*Streethawk Mail.*$",
            "profile": "Work",
        },
        "stevenjose@gmail.com": {
            "calendar_regex": r"stevenjose - Calendar.*$",
            # "profile": "default-release",
            "profile": "Home",
        },
    },
    "volume_up": "pactl set-sink-volume @DEFAULT_SINK@ +5000",
    "volume_down": "pactl set-sink-volume @DEFAULT_SINK@ -5000",
    "group_affinity": {
        "emulator": 3,
        "mail": 11,
        "browser": 11,
        "transgui": 1,
        "devtools": 2,
        "rdesktop": 15,
        "virtualbox": 4,
        "slack": 16,
        "hangouts": 7,
        "discord": 18,
        "zoom": 18,
        "whatsapp": 8,
        "android-studio": 12,
    },
    "pushbullet_api_key": passstore("internet/pushbullet"),
    "brightness_up": "xbacklight -inc 10",
    "brightness_down": "xbacklight -dec 10",
}
series9_config = {
    "laptop": True,
    "autostart-once": laptop_autostart,
    "screen_affinity": {
        "mail": 1,
        "emulator": 2,
    },
    "brightness_up": "sudo /home/steven/.bin/samctl.py -s up",
    "brightness_down": "sudo /home/steven/.bin/samctl.py -s down",
    "kbd_brightness_up": "sudo /home/steven/.bin/samctl.py -k up",
    "kbd_brightness_down": "sudo /home/steven/.bin/samctl.py -skdown",
    "battery": "BAT1",
}
zenbook1 = {
    "laptop": True,
    "battery": "BAT0",
    "kbd_brightness_up": "asus-kbd-backlight up",
    "kbd_brightness_down": "asus-kbd-backlight down",
    "autostart-once": laptop_autostart,
}
razorjack = dict(zenbook1)
razorjack["battery"] = False
yoga0 = {
    "battery": "BAT0",
    "laptop": True,
}

platform_specific = {
    "series9": series9_config,
    "zenbook1": zenbook1,
    "steven-series9": series9_config,
    "razorjack": razorjack,
    "yoga0": yoga0,
}


def get_hostconfig_dict():
    host = platform.node().split(".", 1)[0].lower()
    config = dict(default_config)
    config.update(platform_specific.get(host, default_config))
    return config


def get_hostconfig(key, default=None):
    return get_hostconfig_dict().get(key, default)


def get_screen(index):
    """Get platform specific screen"""
    monitors = get_num_monitors()
    if monitors == 1:
        return 0
    return int(get_hostconfig("screens", {}).get(index, 0))


def get_screen_affinity(app):
    return get_hostconfig("screen_affinity", {}).get(app, 0)


def get_group_affinity(app):
    ret = get_hostconfig("group_affinity", {}).get(app, 0)
    if ret > 9 and get_num_monitors() < 2:
        ret -= 10
    return str(ret)


@lru_cache(maxsize=1)
def get_num_monitors():
    # import Xlib.display
    # display = Xlib.display.Display(':0')
    # return display.screen_count()
    try:
        output = subprocess.Popen(
            'xrandr | grep -e "\ connected" | cut -d" " -f1',
            shell=True,
            stdout=subprocess.PIPE,
        ).communicate()[0]

        displays = output.strip().decode("utf8").split("\n")
        logger.debug("Number of displays detected : %s", displays)
        return len(displays)
    except Exception:
        logging.exception("failed to get number of monitors")
    # for display in displays:
    #    values = display.split('x')
    #    width = values[0]
    #    height = values[1]
    #    print "Width:" + width + ",height:" + height


def hdmi_connected():
    for hdmi in glob.glob("/sys/class/drm/card0/*HDMI-A-1/status"):
        if open(hdmi).read().strip() == "connected":
            logger.info("HDMI connected")
            return True
    return False


def window_exists(qtile, regex):
    for wid, window in get_windows_map(qtile).items():
        if regex.match(window.name):
            logger.debug("Matched %s", str(window))
            return window
    # for window in get_windows_map(qtile).values():
    #    logger.debug("windowname %s", window.name)
    #    if regex.match(str(window.name)):
    #        return window
    #    wm_class = window.window.get_wm_class()
    #    logger.debug(wm_class)
    #    if wm_class and any(map(regex.match, wm_class)):
    #        return window


def execute_once(
    process, process_filter=None, toggle=False, window_regex=None, qtile=None
):
    if not qtile:
        from libqtile import qtile
    cmd = process.split()
    process_filter = process_filter or cmd[0]
    pid = None
    try:
        pid = local["pgrep"]("-f", process_filter)
        pid.wait()
    except Exception as e:
        logger.debug("Not running: %s", process_filter)
    if not pid:
        logger.debug("process not running: %s", process_filter)
        if window_regex and window_exists(qtile, window_regex):
            assert not toggle, "cannot toggle no pid"
            return
        # spawn the process using a shell command with subprocess.Popen
        logger.debug("Starting: %s", cmd)
        try:
            # if qtile:
            qtile.cmd_spawn(process)
            # else:
            #    cmd = local[process]
            #    cmd()
            logger.info("Started: %s: %s", cmd, pid)
        except Exception as e:
            logger.exception("Error running %s", cmd)
    elif toggle:
        logger.debug("Kill process: %s", process_filter)
        os.kill(int(pid), signal.SIGKILL)
    else:
        logger.debug("Not Starting: %s", cmd)


def get_current_screen(qtile):
    try:
        return qtile.current_screen
    except AttributeError:
        return qtile.currentScreen


def get_current_window(qtile):
    try:
        return qtile.current_window
    except AttributeError:
        return qtile.currentWindow


def get_current_group(qtile):
    try:
        return qtile.current_group
    except AttributeError:
        return qtile.currentGroup


def get_windows_map(qtile):
    try:
        return qtile.windows_map
    except AttributeError:
        return qtile.windowMap


def get_redis():
    from redis.client import Redis
    from redis import BlockingConnectionPool

    client = Redis(connection_pool=BlockingConnectionPool())
    return client
