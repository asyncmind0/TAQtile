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
import os
import psutil

from taqtile.log import logger
from taqtile.utils import send_notification


def passstore(path, raise_exception=True):
    try:
        return subprocess.check_output(["pass", path]).strip().decode("utf8")
    except:
        if raise_exception:
            raise
        logger.exception(f"error fetching from pass {path}")


# TODO https://confuse.readthedocs.io/en/latest/

mod = "mod4"

default_config = {
    "screens": {
        0: 1,
        1: 0,
        2: 2,
        3: 3,
    },
    "term0_key": "F11",
    "term1_key": "F12",
    "term2_key": "XF86Launch5",
    "term3_key": "F9",
    "browser_accounts": {
        "melit.stevenjoseph@gmail.com": {
            "calendar": {
                "regex": r"^Google Calendar.*$",
            },
            "mail": {
                "regex": r".*melit\.stevenjoseph@gmail\.com.*$",
            },
            # "profile": "default-release",
            "profile": "Home",
        },
        "steven@stevenjoseph.in": {
            "calendar": {
                "regex": r"^stevenjoseph - Calendar.*$",
            },
            "mail": {
                "regex": r".*steven@stevenjoseph.*$",
            },
            # "profile": "default-release",
            "profile": "Home",
        },
        "stevenjose@gmail.com": {
            "calendar": {"regex": r"stevenjose - Calendar.*$"},
            "mail": {"regex": r".*stevenjose@gmail\.com.*mail\.google\.com.*$"},
            # "profile": "default-release",
            "profile": "Home",
        },
    },
    "volume_up": "pactl set-sink-volume @DEFAULT_SINK@ +1000",
    "volume_down": "pactl set-sink-volume @DEFAULT_SINK@ -1000",
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
    # "pushbullet_api_key": passstore("internet/pushbullet"),
    "brightness_up": "xbacklight -inc 10",
    "brightness_down": "xbacklight -dec 10",
    "autostart-once": {
        # "grafana-bison": None,
        "dropbox": None,
        # "slack": None,
        #'blueman-applet': None,
        #'discord': None,
        #'parcellite': None,
        "insync start": None,
        "feh --bg-scale ~/.wallpaper": None,
        "whatsapp-web-desktop": dict(
            process_filter="whatsapp",
            window_regex=re.compile(r".*whatsapp.*", re.I),
        ),
        'nvidia-settings -a "[gpu:0]/GpuPowerMizerMode=1"': None,
        "discord": None,
        "electrum": None,
        "bitcoin-qt": None,
        "pavucontrol-qt": None,
        "qpwgraph": None,
        # "kdeconnect-app": None,
        # "pasystray": None,
        "antimicrox --tray": None,
        "monero-wallet-gui": None,
    },
}


platform_specific = {
    "zenbook1": {
        "laptop": True,
        "battery": "BAT0",
        "kbd_brightness_up": "asus-kbd-backlight up",
        "kbd_brightness_down": "asus-kbd-backlight down",
    },
    "series9": {
        "laptop": True,
        "screen_affinity": {
            "mail": 1,
            "emulator": 2,
        },
        "brightness_up": "sudo /home/steven/.bin/samctl.py -s up",
        "brightness_down": "sudo /home/steven/.bin/samctl.py -s down",
        "kbd_brightness_up": "sudo /home/steven/.bin/samctl.py -k up",
        "kbd_brightness_down": "sudo /home/steven/.bin/samctl.py -skdown",
        "battery": "BAT1",
    },
    "razorjack": {"battery": False},
    "yoga0": {
        "battery": "BAT0",
        "laptop": True,
    },
    "threadripper0": {"battery": False},
    "doombox": {
        "battery": False,
        "autostart-once": {"/usr/sbin/brave --profile-directory=home": None},
    },
    "surface0": {
        "battery": "BAT1",
        "laptop": True,
    },
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


def hdmi_connected():
    for hdmi in glob.glob("/sys/class/drm/card0/*HDMI-A-1/status"):
        if open(hdmi).read().strip() == "connected":
            logger.info("HDMI connected")
            return True
    return False


def window_exists(qtile, regex):
    for wid, window in get_windows_map(qtile).items():
        try:
            if regex.match(window.name):
                logger.debug("Matched %s", str(window))
                return window
        except:
            pass


def execute_once(
    process, process_filter=None, toggle=False, window_regex=None, qtile=None
):
    if not qtile:
        from libqtile import qtile
    cmd = process.split()
    process_filter = process_filter or cmd[0]
    pid = None
    try:
        pid = local["pgrep"]("-f", process_filter).strip()
    except Exception as e:
        logger.info("process not running: %s", process_filter)
        if window_regex and window_exists(qtile, window_regex):
            assert not toggle, "cannot toggle no pid"
            return
        # spawn the process using a shell command with subprocess.Popen
        logger.debug("Starting: %s", cmd)
        try:
            qtile.cmd_spawn(f"systemd-run --user {process}")
            logger.info("Started: %s: %s", cmd, pid)
        except Exception as e:
            logger.exception("Error running %s", cmd)
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


def show_process_stats(qtile):
    from guppy import hpy

    pid = os.getpid()
    p = psutil.Process(pid)
    threads = p.num_threads()
    mem_info = p.memory_info()
    rss = mem_info.rss / 1024 / 1024  # convert to MB
    vms = mem_info.vms / 1024 / 1024  # convert to MB
    from guppy import hpy

    h = hpy()
    message = f"""
    Process ID: {pid}
    Number of Threads: {threads}
    Resident Set Size: {rss} MB
    Virtual Memory Size: {vms} MB
    {h.heap()}
    """
    logger.info(message)
    send_notification("stats", message)


def group_by_name(groups, name):
    for group in groups:
        if group.name == name:
            return group
