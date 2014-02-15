from libqtile.config import Key, Click, Drag, Screen, Group, Match, Rule
from libqtile.command import lazy, CommandObject
from libqtile import layout, bar, widget

from extra import (SwitchToWindowGroup, check_restart, terminal,
                   SwitchGroup, get_num_monitors)
from screens import get_screens
from keys import get_keys
import logging
import re

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("qtile").setLevel(logging.DEBUG)
log = logging.getLogger('qtile.config')
log.setLevel(logging.DEBUG)
mod = "mod4"
keys = get_keys(mod)

num_screens = get_num_monitors()
log.debug("Num Desktops:%s", num_screens)


def generate_groups(num_screens=1):
    num_groups = num_screens * 10
    log.debug("num_groups:%s", num_groups)
    groups = [Group(str(i)) for i in range(1, num_groups)]
    for i, g in enumerate(groups, 1):
       # mod1 + letter of group = switch to group
        log.debug("group:%s", i)
        if i < 10:
            keys.append(
                Key([mod], str(i), lazy.function(SwitchGroup(str(i)))))
            keys.append(
                Key([mod, "shift"], str(i), lazy.window.togroup(str(i))))
    keys.append(Key([], "F1",      lazy.function(SwitchGroup("1"))))
    keys.append(Key([], "F2",      lazy.function(SwitchGroup("2"))))
    keys.append(Key([], "F6",      lazy.function(SwitchGroup("6"))))
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

# dgroup rules that not belongs to any group
dgroups_app_rules = [
    # Everything i want to be float, but don't want to change group
    Rule(Match(title=["right"]), group="right"),
    Rule(Match(title=["left"]), group="left"),
    Rule(Match(title=['nested', 'gscreenshot'],
               wm_class=['Guake.py', 'Exe', 'Onboard', 'Florence',
                         'Terminal', 'Gpaint', 'Kolourpaint', 'Wrapper',
                         'Gcr-prompter', 'Ghost',
                         re.compile('Gnome-keyring-prompt.*?')],
               ),
         float=True, intrusive=True),

    # floating windows
    Rule(Match(wm_class=['Wine', 'Xephyr']),
         float=True),
    ]

groups = generate_groups(num_screens)

dgroups_key_binder = None
dgroups_app_rules = []

layouts = [
    layout.Max(),
    layout.Stack(stacks=2)
]

screens = get_screens(num_screens)
main = None
# follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating()
mouse = ()
auto_fullscreen = True
widget_defaults = {}
