"""Platform specific configurtation options
"""
import platform

platform_specific = {
    'steven-series9': {'screens': {0: 1, 1: 0}},
    'sydsjoseph-pc1': {'screens': {0: 0, 1: 1}}
}


def get_screen(index):
    """Get platform specific screen """
    host = platform.node().split('.', 1)[0].lower()
    return platform_specific[host]['screens'][index]
