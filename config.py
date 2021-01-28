# TODO handle MultiScreenGroupBox clicks and events
import logging
import os
from os.path import expanduser
from log import init_log
logger = init_log(
    log_level=logging.DEBUG,
)

from libqtile import layout
from libqtile.command import lazy
from libqtile.config import Click, Drag

from groups import generate_groups
from keys import get_keys
from screens import get_screens
from system import get_num_monitors
from themes import current_theme

mod = "mod4"
num_monitors = get_num_monitors()

layouts = [
    layout.Max(**current_theme),
    layout.Stack(**current_theme),
    layout.xmonad.MonadTall(ratio=0.50, **current_theme),
    layout.Tile(**current_theme),
    layout.Zoomy(**current_theme),
    # layout.TreeTab(),
    # a layout just for gimp
    # layout.Slice('term1', 192, name='gimp', role='gimp-toolbox',
    #             fallback=layout.Slice('right', 256, role='gimp-dock',
    #                                   fallback=layout.Stack(
    #                                       num_stacks=1, **border_args))),
]

# Automatically float these types. This overrides the default behavior (which
# is to also float utility types), but the default behavior breaks our fancy
# gimp slice layout specified later on.
floating_layout = layout.Floating(
    float_rules=[
        {'wname': 'shrapnel'},
        {'wname': 'Copying'},
        {'wmclass': 'Kgpg'},
        #{'wmclass': 'Insync.py'},
    ],
    auto_float_types=[
        "notification",
        "toolbar",
        "splash",
        'dialog',  # this has to be here else dialogs go to new group
        "Screenkey",
    ], **current_theme)


# This allows you to drag windows around with the mouse if you want.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    #Click([mod], "Button2", lazy.window.bring_to_front())
]

float_windows = ['buddy_list', ]
follow_mouse_focus = True
bring_front_click = True
cursor_warp = False
auto_fullscreen = True
widget_defaults = current_theme
dgroups_app_rules = []
num_groups = num_monitors * 10

groups = generate_groups(
    num_groups, num_monitors, dgroups_app_rules, layouts)
keys = get_keys(mod, num_groups, num_monitors)
screens = get_screens(num_monitors, num_groups, groups)


class NoTimerFilter(logging.Filter):
    def filter(self, record):
        return 'timer' not in record.getMessage()

def main(self):
    self.logger = init_log(
        log_level=logging.DEBUG,
    )


import hooks
