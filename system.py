"""Platform specific configurtation options
"""
import platform

platform_specific = {
    'steven-series9': {
        'screens': {0: 1, 1: 0},
        'battery': True,
        'laptop': True
    },
    'sydsjoseph-pc1': {
        'screens': {0: 0, 1: 1},
        'battery': False,
        'laptop': False
    }
}


host = platform.node().split('.', 1)[0].lower()


def get_hostconfig(key):
    return platform_specific[host][key]


def get_screen(index):
    """Get platform specific screen """
    return get_hostconfig('screens')[index]
