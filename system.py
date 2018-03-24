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
    #'xcompmgr': None,
    #'klipper': None,
    #'xscreensaver -nosplash': None,
    expanduser('~/.bin/xstartup'): None,
#    'setxkbmap -option \'ctrl:swapcaps\'': None,
}

laptop_autostart = dict(common_autostart)
laptop_autostart.update({
    'blueman-applet': None,
    'redshift-gtk': None,
    'insync start': None,
    #'parcellite': None,
    '/opt/trinity/bin/klipper': None,
    'slack': None,
    'yakyak': None,
    #'discord-canary': None,
    'feh --bg-scale ~/.wallpaper': None,
    'whatsapp-web-desktop': dict(
        process_filter="whatsapp",
        window_regex=re.compile(r".*whatsapp.*", re.I),
    )
})

desktop_autostart = dict(common_autostart)
desktop_autostart.update({
    'jabberel-tray.py': None})
default_config = {
    'term1_key': 'F11',
    'term2_key': 'F12',
    'term3_key': 'F9',
    'term4_key': 'F10',
}
iress_config = {
    'screens': {0: 0, 1: 1},
    'battery': False,
    'laptop': False,
    'autostart-once': common_autostart,
    'screen_affinity': {
        'mail': 1,
        },
    'group_affinity': {
        'mail': 1,
        'browser': 1,
        'virtualbox': 4,
        'rdesktop': 5,
    },
    'term1_key': 'XF86Launch5',
    'term2_key': 'XF86Launch6',
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
    'group_affinity': {
        'emulator': 3,
        'mail': 1,
        'browser': 11,
        'transgui': 1,
        'devtools': 2,
        'rdesktop': 15,
        'virtualbox': 4,
        'slack': 6,
        'hangouts': 7,
        'discord': 8,
    },
    'term1_key': 'F11',
    'term2_key': 'F12',
    'term3_key': 'F9',
    'term4_key': 'F10',
}

platform_specific = {
    'steven-series9': series9_config,
    'sydsjoseph-pc1': iress_config,
    'au02-sjosephpc2': iress_config,
}


host = platform.node().split('.', 1)[0].lower()


def get_hostconfig(key, default=None):
    return platform_specific.get(host, default_config).get(key, default)


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
    for window in qtile.windowMap.values():
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
