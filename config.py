from libqtile.config import Key, Click, Drag, Screen, Group, Match, Rule
from libqtile.command import lazy
from libqtile import layout, bar, widget

from extra import SwitchToWindowGroup, check_restart, terminal
from screens import get_screens
from keys import get_keys
import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("qtile").setLevel(logging.INFO)

mod = "mod4"
keys = get_keys(mod)


def generate_groups():
    groups = [Group(str(i)) for i in range(1, 10)]
    for i in groups:
        # mod1 + letter of group = switch to group
        keys.append(
            Key([mod], i.name, lazy.group[i.name].toscreen())
        )
        # mod1 + shift + letter of group = switch to & move focused window to
        # group
        keys.append(
            Key([mod, "shift"], i.name, lazy.window.togroup(i.name)))
    groups.append(
        Group('left', exclusive=True,
              spawn=terminal("left"),
              matches=[Match(title=[".*left.*"],
                             wm_class=["InputOutput"])]))
    groups.append(
        Group('right', exclusive=True,
              spawn=terminal("right"),
              matches=[Match(title=[".*right.*"],
                             wm_class=["InputOutput"])]))
    return groups


groups = generate_groups()

dgroups_key_binder = None
dgroups_app_rules = []

layouts = [
    layout.Max(),
    layout.Stack(stacks=2)
]

screens = get_screens()
main = None
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating()
mouse = ()
auto_fullscreen = True
widget_defaults = {}
