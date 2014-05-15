"""Platform specific configurtation options
"""
import platform

common_autostart = [
    'parcellite',
    'bluetooth-applet',
    'nitrogen --restore',
    'xscreensaver -nosplash',
    'dropboxd',
]

platform_specific = {
    'steven-series9': {
        'screens': {0: 1, 1: 0},
        'battery': True,
        'laptop': True,
        'autostart-once': common_autostart + [
            'batterymon -t 16x16',
            'nm-applet',
        ],
        'screen_preferences':{
            2:[{'wmclass': "google-chrome-stable"}, {"wmclass": "Navigator"}],
            1:[]
        }
    },
    'sydsjoseph-pc1': {
        'screens': {0: 0, 1: 1},
        'battery': False,
        'laptop': False,
        'autostart-once': common_autostart + [
        ],
        'screen_preferences':{}
    }
}


host = platform.node().split('.', 1)[0].lower()


def get_hostconfig(key):
    return platform_specific[host][key]


def get_screen(index):
    """Get platform specific screen """
    return get_hostconfig('screens')[index]
