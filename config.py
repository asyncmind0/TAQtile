from libqtile.config import Key, Click, Drag, Screen, Group, Match, Rule
from libqtile.command import lazy, CommandObject
from libqtile import layout, bar, widget, hook

from extra import (SwitchToWindowGroup, check_restart, terminal,
                   SwitchGroup, get_num_monitors, execute_once, MoveToGroup)
from screens import get_screens
from keys import get_keys
import logging
import os
import re
# http://stackoverflow.com/questions/6442428/how-to-use-popen-to-run-backgroud-process-and-avoid-zombie
import signal
signal.signal(signal.SIGCHLD, signal.SIG_IGN)

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("qtile").setLevel(logging.WARN)
log = logging.getLogger('qtile.config')
log.setLevel(logging.DEBUG)
mod = "mod4"
keys = get_keys(mod)

num_screens = get_num_monitors()
log.debug("Num Desktops:%s", num_screens)

#TODO send new clients to group 1 if current group is special group
#TODO handle MultiScreenGroupBox clicks and events
#TODO handle screen preference for windows


def generate_groups(num_screens=1):
    num_groups = num_screens * 10
    log.debug("num_groups:%s", num_groups)
    groups = [Group(str(i)) for i in range(1, num_groups)]
    for i, g in enumerate(groups, 1):
       # mod1 + letter of group = switch to group
        #log.debug("group:%s", i)
        if i < 10:
            keys.append(
                Key([mod], str(i), lazy.function(SwitchGroup(i))))
            keys.append(
                Key([mod, "shift"], str(i),
                    lazy.function(MoveToGroup(i))))
    keys.append(Key([], "F1",      lazy.function(SwitchGroup("1"))))
    keys.append(Key([], "F2",      lazy.function(SwitchGroup("2"))))
    keys.append(Key([], "F10",      lazy.function(SwitchGroup("4", 0))))
    keys.append(Key([], "F9",      lazy.function(SwitchGroup("3", 0))))
    groups.append(
        Group('left', exclusive=False,
              spawn=terminal("left"),
              matches=[Match(title=[".*left.*"],
                             wm_class=["InputOutput"])]))
    groups.append(
        Group('right', exclusive=False,
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
    Rule(Match(wm_class=["Pavucontrol", 'Wine', 'Xephyr']),
         float=True),
    Rule(Match(title=["Hangouts"]), group="6"),
    Rule(Match(wm_class=["Kmail"]), group="4"),
    Rule(Match(wm_class=["Pidgin"]), group="3"),
    ]

# Automatically float these types. This overrides the default behavior (which
# is to also float utility types), but the default behavior breaks our fancy
# gimp slice layout specified later on.
floating_layout = layout.Floating(auto_float_types=[
    "notification",
    "toolbar",
    "splash",
    "dialog"
])

groups = generate_groups(num_screens)

dgroups_key_binder = None

border_args = dict(
    border_width=1,
)
layouts = [
    layout.Max(),
    layout.Stack(stacks=2),
    layout.xmonad.MonadTall(ratio=0.50),
    layout.TreeTab(),
    layout.Zoomy(),
    # a layout just for gimp
    layout.Slice('left', 192, name='gimp', role='gimp-toolbox',
                 fallback=layout.Slice('right', 256, role='gimp-dock',
                                       fallback=layout.Stack(
                                           stacks=1, **border_args))),
    # a layout for pidgin
    layout.Slice('right', 256, role='buddy_list',
                 fallback=layout.Stack(stacks=1, **border_args)),
    # a layout for hangouts
    layout.Slice('right', 256, wname="Hangouts",
                 fallback=layout.Stack(stacks=1, **border_args)),
]


@hook.subscribe.screen_change
def restart_on_randr(qtile, ev):
    log.debug(ev)
    import subprocess
    commands = []
    if len(qtile.screens) > 1:
        commands.append(os.path.expanduser("~/bin/dualmonitor"))
    else:
        commands.append(os.path.expanduser("~/bin/rightmonitor"))
    commands.extend([
        "xset b 5 6000 600",
        "xset r rate 150 40",
        "xmodmap ~/.xmodmap",
        "xsetroot -cursor_name left_ptr",
        'nitrogen --restore',
    ])
    for cmd in commands:
        subprocess.Popen(cmd.split())
    qtile.cmd_restart()


@hook.subscribe.startup
def startup():
    import subprocess
    from extra import execute_once
    commands = [
        "xsetroot -cursor_name left_ptr",
        'nitrogen --restore'
    ]
    for cmd in commands:
        subprocess.Popen(cmd.split())
    execute_once('parcellite')
    # execute_once('firefox')


@hook.subscribe.client_new
def on_client_new(window):
    log.debug(window.group)
    #window.togroup(qtile.currentGroup)
    pass

float_windows = []


def should_be_floating(w):
    wm_class = w.get_wm_class()
    if isinstance(wm_class, tuple):
        for cls in wm_class:
            if cls.lower() in float_windows:
                return True
    else:
        if wm_class.lower() in float_windows:
            return True
    return w.get_wm_type() == 'dialog' or bool(w.get_wm_transient_for())


@hook.subscribe.client_new
def dialogs(window):
    if should_be_floating(window.window):
        window.floating = True

screens = get_screens(num_screens)
main = None
# follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
mouse = ()
auto_fullscreen = True
widget_defaults = {}
