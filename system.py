"""Platform specific configurtation options
"""
import logging
import platform
import sh
import subprocess

log = logging.getLogger('qtile')

mod = "mod4"

common_autostart = {
    'xcompmgr': None,
    'klipper': None,
    'xscreensaver -nosplash': None,
    'dropbox start': 'dropbox',
    'insync start': 'insync',
    'bluedevil-monolithic': 'bluedevil-monol',
    '~/.bin/xstartup': None,
    '/usr/bin/start-pulseaudio-x11': 'pulseaudio',
    'kmix': None,
}

laptop_autostart = dict(common_autostart)
laptop_autostart.update({
    'nm-applet': None})

desktop_autostart = dict(common_autostart)
desktop_autostart.update({
    'jabberel-tray.py': None})


platform_specific = {
    'steven-series9': {
        'screens': {0: 0, 1: 1},
        'battery': True,
        'laptop': True,
        'autostart-once': laptop_autostart,
        'screen_affinity': {
        },
        'term1_key': 'F11',
        'term2_key': 'F12',
    },
    'sydsjoseph-pc1': {
        'screens': {0: 0, 1: 1},
        'battery': False,
        'laptop': False,
        'autostart-once': common_autostart,
        'screen_affinity': {
            'mail': 1
        },
        'term1_key': 'XF86Launch5',
        'term2_key': 'XF86Launch6',
    }
}


host = platform.node().split('.', 1)[0].lower()


def get_hostconfig(key):
    return platform_specific[host][key]


def get_screen(index):
    """Get platform specific screen """
    return get_hostconfig('screens')[index]


def get_num_monitors():
    #import Xlib.display
    #display = Xlib.display.Display(':0')
    #return display.screen_count()
    output = subprocess.Popen(
        'xrandr | grep -e "\ connected" | cut -d" " -f1',
        shell=True, stdout=subprocess.PIPE).communicate()[0]

    displays = output.strip().split('\n')
    log.debug(displays)
    return len(displays)
    #for display in displays:
    #    values = display.split('x')
    #    width = values[0]
    #    height = values[1]
    #    print "Width:" + width + ",height:" + height


def execute_once(process, process_filter=None, qtile=None):
    cmd = process.split()
    process_filter = process_filter or cmd[0]
    pid = None
    try:
        pid = sh.pgrep("-f", process_filter)
        pid.wait()
    except Exception as e:
        log.error("CalledProcessError")
    if not pid:
        # spawn the process using a shell command with subprocess.Popen
        log.debug("Starting: %s", cmd)
        try:
            if qtile:
                qtile.cmd_spawn(process)
            else:
                cmd = sh.Command(process)
                cmd()
            log.info("Started: %s: %s", cmd, pid)
        except Exception as e:
            log.error("Error running %s", cmd)
