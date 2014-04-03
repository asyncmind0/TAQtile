from libqtile.config import Key, Click, Drag, Screen, Group, Match, Rule
from libqtile.command import lazy
from libqtile import layout, bar, widget
from extra import (SwitchToWindowGroup, check_restart,
                   terminal, MoveToOtherScreenGroup, SwitchGroup)
from screens import PRIMARY_SCREEN, SECONDARY_SCREEN
from system import get_hostconfig


def get_keys(mod):
    keys = [
        # Switch between windows in current stack pane
        ([mod], "k", lazy.layout.next().when('stack'),
         lazy.layout.down()),
        ([mod], "j", lazy.layout.previous().when('stack'),
         lazy.layout.up()),
        ([mod, "shift"], "l", lazy.layout.client_to_next().when('stack'),
         lazy.layout.down()),
        ([mod, "shift"], "h", lazy.layout.client_to_previous().when('stack'),
         lazy.layout.up()),
        ([mod], "h", lazy.layout.previous().when('tile'),
         lazy.layout.up().when('xmonad-tall')),
        ([mod], "l", lazy.layout.next().when('tile'),
         lazy.layout.down().when('xmonad-tall')),
        # Move windows up or down in current stack
        ([mod, "shift"], "k", lazy.layout.shuffle_down()),
        ([mod, "shift"], "j", lazy.layout.shuffle_up()),

        # Swap panes of split stack
        ([mod, "shift"], "space", lazy.layout.rotate()),
        # toggle between windows just like in unity with 'alt+tab'
        (["mod1", "shift"], "Tab", lazy.layout.down()),
        (["mod1"], "Tab", lazy.layout.up()),
        ([mod, "shift"], "comma",
         lazy.function(MoveToOtherScreenGroup(prev=True))),
        ([mod, "shift"], "period",
         lazy.function(MoveToOtherScreenGroup(prev=False))),
        # Toggle between split and unsplit sides of stack.
        # Split = all windows displayed
        # Unsplit = 1 window displayed, like Max layout, but still with
        # multiple stack panes
        ([mod, "shift"], "Return", lazy.layout.toggle_split()),
        ([mod], "Return", lazy.spawn("st")),
        (["shift", mod], "q", lazy.shutdown()),
        # Toggle between different layouts as defined below
        ([mod], "space",    lazy.nextlayout()),
        ([mod], "q",      lazy.window.kill()),
        # Key([mod, "control"], "r", lazy.restart()),
        ([mod, "control"], "r", lazy.function(check_restart)),
        #([mod], "r", lazy.spawncmd()),
        ([mod], "F2", lazy.spawn("dmenu_run -f -l 20")),
        ([mod], "r", lazy.spawncmd()),
        ([], "F11", lazy.function(
            SwitchToWindowGroup("left", terminal("left"), PRIMARY_SCREEN))),
        ([], "F12", lazy.function(
            SwitchToWindowGroup(
                "right", terminal("right"), SECONDARY_SCREEN))),
        ([mod], "Right", lazy.screen.nextgroup()),
        ([mod], "Left", lazy.screen.prevgroup()),
        ([], "F6",      lazy.function(SwitchGroup("6", PRIMARY_SCREEN))),
        # app launcher
        ([mod, "shift"], "b", lazy.spawn("conkeror")),
        ([mod, "shift"], "g", lazy.spawn("google-chrome-stable")),
        ([mod, "control"], "l", lazy.spawn("xscreensaver-command -lock")),
        ([mod], "m", lazy.group.setlayout('max')),
        ([mod], "t", lazy.group.setlayout('stack')),
        ([mod], "f", lazy.group.setlayout('float')),
        #([mod], "t", lazy.group.setlayout('xmonad-tall')),
        #([], "3270_PrintScreen", lazy.spawn("ksnapshot")),
        ([mod, "shift"], "s", lazy.spawn("ksnapshot")),
        ([mod, "shift"], "k", lazy.spawn("xkill")),
    ]
    laptop_keys = [
        # laptop keys
        ([], "XF86MonBrightnessUp", lazy.spawn("sudo ~/bin/samctl.py -s up")),
        ([], "XF86MonBrightnessDown", lazy.spawn(
            "sudo ~/bin/samctl.py -s down")),
        ([], "XF86KbdBrightnessUp", lazy.spawn("sudo ~/bin/samctl.py -k up")),
        ([], "XF86KbdBrightnessDown", lazy.spawn(
            "sudo ~/bin/samctl.py -k down")),
        ([], "XF86AudioLowerVolume", lazy.spawn("sudo ~/bin/samctl.py -k up")),
        ([], "XF86AudioRaiseVolume", lazy.spawn(
            "sudo ~/bin/samctl.py -v down")),
    ]
    if get_hostconfig('laptop'):
        keys.extend(laptop_keys)
    return [Key(*k) for k in keys]
