"""Platform specific configurtation options
"""
import logging
import platform
from plumbum import local
import subprocess
import signal
from os.path import expanduser
from log import logger
import os
import re
import glob


mod = "mod4"

common_autostart = {
    'xcompmgr': None,
    #'klipper': None,
    'xscreensaver -nosplash': None,
    expanduser('~/.bin/xstartup'): None,
    'xset s off -dpms': None,
    'setxkbmap -option \'ctrl:swapcaps\'': None,
}

laptop_autostart = dict(common_autostart)
laptop_autostart.update({
    "nm-applet": None,
    'blueman-applet': None,
    #'redshift-gtk': None,
    'insync start': None,
    #'parcellite': None,
    'slack': None,
    'feh --bg-scale ~/.wallpaper': None,
    'whatsapp-web-desktop': dict(
        process_filter="whatsapp",
        window_regex=re.compile(r".*whatsapp.*", re.I),
    )
})

desktop_autostart = dict(common_autostart)
desktop_autostart.update({
    'jabberel-tray.py': None
})
default_config = {
    'term1_key': 'F11',
    'term2_key': 'F12',
    'term3_key': 'F9',
    'term4_key': 'F10',
    'google_accounts': [
        'melit.stevenjoseph@gmail.com',
        'steven@stevenjoseph.in',
        'steven@streethawk.co',
        'stevenjose@gmail.com',
    ],
    'volume_up': 'pactl set-sink-volume @DEFAULT_SINK@ +5000',
    'volume_down': 'pactl set-sink-volume @DEFAULT_SINK@ -5000',
    'group_affinity': {
        'emulator': 3,
        'mail': 1,
        'browser': 11,
        'transgui': 1,
        'devtools': 2,
        'rdesktop': 15,
        'virtualbox': 4,
        'slack': 16,
        'hangouts': 7,
        'discord': 8,
        'whatsapp': 8,
        'android-studio': 12
    },
}
series9_config = {
    'screens': {0: 1, 1: 0},
    'battery': True,
    'laptop': True,
    'autostart-once': laptop_autostart,
    'screen_affinity': {
        'mail': 1,
        'emulator': 2,
    },
    'brightness_up': "sudo /home/steven/.bin/samctl.py -s up",
    'brightness_down': "sudo /home/steven/.bin/samctl.py -s down",
    'kbd_brightness_up': "sudo /home/steven/.bin/samctl.py -k up",
    'kbd_brightness_down': "sudo /home/steven/.bin/samctl.py -skdown",
    'battery': 'BAT1',
    'dual_monitor': 'xrandr --output LVDS1 --noprimary --mode 1600x900 --output HDMI1 --mode 1920x1080 --left-of LVDS1 --rotate normal',
    'single_monitor': "xrandr --output LVDS1 --mode 1600x900 --output HDMI-1 --off",
}

zenbook1 = {
    'screens': {0: 1, 1: 0},
    'laptop': True,
    'battery': 'BAT0',
    'brightness_up': "xbacklight -inc 10",
    'brightness_down': "xbacklight -dec 10",
    'kbd_brightness_up': "asus-kbd-backlight up",
    'kbd_brightness_down': "asus-kbd-backlight down",
    'dual_monitor': "xrandr --output eDP-1 --noprimary --mode 1600x900 --output HDMI-1 --mode 1920x1080 --left-of eDP-1 --rotate normal",
    'single_monitor': "xrandr --output eDP-1 --mode 1600x900 --output HDMI-1 --off",
    'autostart-once': laptop_autostart,
}

platform_specific = {
    'series9': series9_config,
    'zenbook1': zenbook1,
    'steven-series9': series9_config,
}


host = platform.node().split('.', 1)[0].lower()


def get_hostconfig(key, default=None):
    config = dict(default_config)
    config.update(platform_specific.get(host, default_config))
    return config.get(key, default)


def get_screen(index):
    """Get platform specific screen """
    monitors = get_num_monitors()
    if monitors == 1:
        return 0
    return get_hostconfig('screens', {}).get(index, 0)


def get_screen_affinity(app):
    return get_hostconfig('screen_affinity', {}).get(app, 0)


def get_group_affinity(app):
    ret = get_hostconfig('group_affinity', {}).get(app, 0)
    if ret > 9 and get_num_monitors() < 2:
        ret -= 10
    return str(ret)


def get_num_monitors():
    #import Xlib.display
    #display = Xlib.display.Display(':0')
    #return display.screen_count()
    try:
        output = subprocess.Popen(
            'xrandr | grep -e "\ connected" | cut -d" " -f1',
            shell=True, stdout=subprocess.PIPE).communicate()[0]

        displays = output.strip().decode('utf8').split('\n')
        logger.debug(displays)
        return len(displays)
    except Exception:
        logging.exception("failed to get number of monitors")
    #for display in displays:
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
    for window in qtile.windows_map.values():
        if regex.match(window.name):
            return True
        wm_class = window.window.get_wm_class()
        logger.debug(wm_class)
        if wm_class and any(map(regex.match, wm_class)):
            return True
    return False


def execute_once(
        process, process_filter=None, qtile=None,
        toggle=False, window_regex=None):
    cmd = process.split()
    process_filter = process_filter or cmd[0]
    pid = None
    try:
        pid = local['pgrep']("-f", process_filter)
        pid.wait()
    except Exception as e:
        logger.debug("Not running: %s", process_filter)
    if not pid:
        if window_regex and window_exists(qtile, window_regex):
            assert not toggle, "cannot toggle no pid"
            return
        # spawn the process using a shell command with subprocess.Popen
        logger.debug("Starting: %s", cmd)
        try:
            if qtile:
                qtile.cmd_spawn(process)
            else:
                cmd = local[process]
                cmd()
            logger.info("Started: %s: %s", cmd, pid)
        except Exception as e:
            logger.error("Error running %s", cmd)
    elif toggle:
        os.kill(int(pid), signal.SIGKILL)

