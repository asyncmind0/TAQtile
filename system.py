"""Platform specific configurtation options
"""
import platform

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
