"""Platform specific configurtation options
"""
import platform
import subprocess
import logging

log = logging.getLogger('qtile.config')
common_autostart = {
    'parcellite': None,
    'bluetooth-applet': None,
    'nitrogen --restore': None,
    'xscreensaver -nosplash': None,
    'dropboxd': 'dropbox',
    'insync start': 'insync',
}

laptop_autostart = dict(common_autostart)
laptop_autostart.update({
    'nm-applet': None})

platform_specific = {
    'steven-series9': {
        'screens': {0: 1, 1: 0},
        'battery': True,
        'laptop': True,
        'autostart-once': laptop_autostart,
        'screen_preferences': {
            2: [{'wmclass': "google-chrome-stable"},
                {"wmclass": "Navigator"}],
            1: []
        }
    },
    'sydsjoseph-pc1': {
        'screens': {0: 0, 1: 1},
        'battery': False,
        'laptop': False,
        'autostart-once': common_autostart,
        'screen_preferences': {}
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

def execute_once(process, process_filter=None):
    cmd = process.split()
    process_filter = process_filter or cmd[0]
    try:
        pid = subprocess.check_output(
            ["pidof", "-s", "-x", process_filter])
    except Exception as e:
        log.exception("CalledProcessError")
    if not pid:
        # spawn the process using a shell command with subprocess.Popen
        log.debug("Starting: %s", cmd)
        pid = subprocess.Popen(
            process, shell=True, close_fds=True,
            stdin=subprocess.PIPE).pid
        log.debug("Started: %s: %s", cmd, pid)
