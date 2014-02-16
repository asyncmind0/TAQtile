"""Platform specific configurtation options
"""
import platform

platform_specific = {
    'steven-series9': {'screens': {0: 1, 1: 0}},
    'sydsjoseph-pc1': {'screens': {0: 1, 1: 0}}
}


def get_screen(index):
    """Get platform specific screen """
    return platform_specific[platform.node()]['screens'][index]