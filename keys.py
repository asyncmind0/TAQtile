from libqtile.config import Key, Click, Drag, Screen, Group, Match, Rule
from libqtile.command import lazy
from libqtile import layout, bar, widget
from extra import (SwitchToWindowGroup, check_restart,
                   terminal, MoveToOtherScreenGroup, SwitchGroup)
from screens import PRIMARY_SCREEN, SECONDARY_SCREEN
from system import get_hostconfig


def get_keys(mod):
    is_laptop = get_hostconfig('laptop')
    left_termkey = "F11"if is_laptop else "F12"
    right_termkey = "F12" if is_laptop else "XF86Eject"
    left_remote_termkey = "F11"if is_laptop else "F12"
    right_remote_termkey = "F12" if is_laptop else "XF86Eject"
    keys = [
        # Switch between windows in current stack pane
        ([mod], "k",
         lazy.layout.up(),
         lazy.layout.previous().when('monadtall')),
        ([mod], "j", 
         lazy.layout.down(),
         lazy.layout.next().when('monadtall')),

        # Move windows up or down in current stack
        ([mod, "shift"], "k", lazy.layout.shuffle_up()),
        ([mod, "shift"], "j", lazy.layout.shuffle_down()),

        ([mod], "h", 
         lazy.layout.up().when('monadtall'),
         lazy.layout.previous()),
        ([mod], "l", 
         lazy.layout.down().when('monadtall'),
         lazy.layout.next()),

        ([mod, "shift"], "l", 
         lazy.layout.client_to_next().when('stack'),
         lazy.layout.increase_ratio().when('tile')),
        ([mod, "shift"], "h", 
         lazy.layout.client_to_previous().when('stack'),
         lazy.layout.decrease_ratio().when('tile')),

        ([mod, "shift"], "space", lazy.layout.flip().when('monadtall'),
         lazy.layout.rotate().when('tile')),

        # Swap panes of split stack
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
        (["shift", mod], "q", lazy.shutdown()),
        # Toggle between different layouts as defined below
        ([mod], "space",    lazy.nextlayout()),
        ([mod], "q",      lazy.window.kill()),
        # Key([mod, "control"], "r", lazy.restart()),
        ([mod, "control"], "r", lazy.function(check_restart)),
        ([mod], "Right", lazy.screen.nextgroup()),
        ([mod], "Left", lazy.screen.prevgroup()),
        ([], "F6",      lazy.function(SwitchGroup("6", PRIMARY_SCREEN))),

        ([mod], "m", lazy.group.setlayout('max')),
        ([mod], "t", lazy.group.setlayout('tile')),
        ([mod], "s", lazy.group.setlayout('stack')),
        ([mod], "x", lazy.group.setlayout('monadtall')),
        ([mod], "f", lazy.window.toggle_floating()),
        #([mod], "t", lazy.group.setlayout('xmonad-tall')),

        # APP LAUNCHERS
        #([mod], "r", lazy.spawncmd()),
        ([mod], "F2", lazy.spawn("dmenu_run -f -l 20")),
        ([mod], "r", lazy.spawncmd()),
        ([mod], "Return", lazy.spawn("st")),
        ([mod, "shift"], "b", lazy.spawn("conkeror")),
        ([mod, "shift"], "g", lazy.spawn("google-chrome-stable")),
        ([mod, "control"], "l", lazy.spawn("xscreensaver-command -lock")),
        #([], "3270_PrintScreen", lazy.spawn("ksnapshot")),
        ([mod, "shift"], "s", lazy.spawn("ksnapshot")),
        ([mod, "control"], "Escape", lazy.spawn("xkill")),
        ([], left_termkey, lazy.function(
            SwitchToWindowGroup("left", terminal("left"), PRIMARY_SCREEN))),
        ([], right_termkey, lazy.function(
            SwitchToWindowGroup("right", terminal("right"), SECONDARY_SCREEN))),
        ([mod], left_remote_termkey, lazy.function(
            SwitchToWindowGroup("remote_left", "st -t remote_left ", PRIMARY_SCREEN))),
        ([mod], right_remote_termkey, lazy.function(
            SwitchToWindowGroup("remote_right", "st -t remote_right", SECONDARY_SCREEN))),
    ]
    laptop_keys = [
        # laptop keys
        ([], "XF86MonBrightnessUp", lazy.spawn("sudo samctl.py -s up")),
        ([], "XF86MonBrightnessDown", lazy.spawn(
            "sudo samctl.py -s down")),
        ([], "XF86KbdBrightnessUp", lazy.spawn("sudo samctl.py -k up")),
        ([], "XF86KbdBrightnessDown", lazy.spawn(
            "sudo samctl.py -k down")),
        ([], "XF86AudioLowerVolume", lazy.spawn("sudo samctl.py -k up")),
        ([], "XF86AudioRaiseVolume", lazy.spawn(
            "sudo samctl.py -v down")),
        ([], "XF86WLAN", lazy.spawn(
            "nmcli con up id Xperia\ Z1\ Network --nowait")),
    ]
    if is_laptop:
        keys.extend(laptop_keys)
    return [Key(*k) for k in keys]
