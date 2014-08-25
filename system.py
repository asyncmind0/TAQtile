"""Platform specific configurtation options
"""
import platform
import subprocess
import logging as log
mod= "mod4"

common_autostart = {
    'klipper': None,
    'xscreensaver -nosplash': None,
    'dropbox start': 'dropbox',
    'insync start': 'insync',
    'bluedevil-monolithic': 'bluedevil-monol'
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
        },
        'left_termkey': ([], "F11"),
        'right_termkey': ([], "F12"),
        'left_remote_termkey': ([mod], "F11"),
        'right_remote_termkey': ([mod], "F12"),
        'monitor_key': ([], "XF86Eject"),
    },
    'sydsjoseph-pc1': {
        'screens': {0: 0, 1: 1},
        'battery': False,
        'laptop': False,
        'autostart-once': common_autostart,
        'screen_preferences': {},
        'left_termkey': ([], "XF86Launch5"),
        'right_termkey': ([], "XF86Launch6"),
        'left_remote_termkey': ([], "XF86Launch9"),
        'right_remote_termkey': ([], "F19"),
        'monitor_key': ([], "XF86Eject"),
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
        pid = subprocess.check_output(
            ["pgrep", "-f", process_filter])
    except Exception as e:
        log.exception("CalledProcessError")
    if not pid:
        # spawn the process using a shell command with subprocess.Popen
        log.debug("Starting: %s", cmd)
        if qtile:
            qtile.cmd_spawn(process)
        else:
            pid = subprocess.Popen(
                process, shell=True, close_fds=True,
                stdin=subprocess.PIPE).pid
        log.debug("Started: %s: %s", cmd, pid)
