# TODO handle MultiScreenGroupBox clicks and events
from libqtile.config import Click, Drag
from libqtile.command import lazy
from libqtile import layout
import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("qtile").setLevel(logging.WARN)
log = logging.getLogger('qtile.config')
log.setLevel(logging.DEBUG)

from system import get_num_monitors
num_monitors = get_num_monitors()
log.debug("Num Desktops:%s", num_monitors)


layouts = [
    layout.Max(),
    layout.Stack(),
    layout.xmonad.MonadTall(ratio=0.50),
    layout.Tile(),
    layout.Zoomy(),
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
])

mod = "mod4"

# This allows you to drag windows around with the mouse if you want.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front())
]

groups = []
float_windows = []
main = None
# follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
auto_fullscreen = True
widget_defaults = {}

from screens import get_screens
from groups import generate_groups
from keys import get_keys

keys = get_keys(mod, groups)
groups = generate_groups(num_monitors, keys) + groups
screens = get_screens(num_monitors)

import hooks
