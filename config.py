# TODO handle MultiScreenGroupBox clicks and events
from libqtile.config import Click, Drag
from libqtile.command import lazy
from libqtile import layout
from libqtile.log_utils import init_log
import os
import logging
init_log(log_level=logging.DEBUG, log_path=os.path.expanduser("~/.qtile.log"))

mod = "mod4"
from system import get_num_monitors
num_monitors = get_num_monitors()
logging.debug("Num Desktops:%s", num_monitors)

from themes import current_theme

layouts = [
    layout.Max(**current_theme),
    layout.Stack(**current_theme),
    layout.xmonad.MonadTall(ratio=0.50, **current_theme),
    layout.Tile(**current_theme),
    layout.Zoomy(**current_theme),
    # layout.TreeTab(),
    # a layout just for gimp
    # layout.Slice('left', 192, name='gimp', role='gimp-toolbox',
    #             fallback=layout.Slice('right', 256, role='gimp-dock',
    #                                   fallback=layout.Stack(
    #                                       num_stacks=1, **border_args))),
]

# Automatically float these types. This overrides the default behavior (which
# is to also float utility types), but the default behavior breaks our fancy
# gimp slice layout specified later on.
floating_layout = layout.Floating(auto_float_types=[
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
    Click([mod], "Button2", lazy.window.bring_to_front())
]

groups = []
float_windows = ['buddy_list', ]
# follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
auto_fullscreen = True
widget_defaults = {}
dgroups_app_rules = []

from screens import get_screens
from groups import generate_groups
from keys import get_keys

keys = get_keys(mod, groups, dgroups_app_rules)
groups = generate_groups(num_monitors, keys, dgroups_app_rules) + groups
screens = get_screens(num_monitors)

import hooks


def main(self):
    pass
