import logging
from libqtile.command import lazy
from libqtile.config import Key, Match, Rule
from extra import (SwitchToWindowGroup, check_restart,
                   terminal, MoveToOtherScreenGroup, SwitchGroup,
                   RaiseWindowOrSpawn, list_windows, list_windows_group,
                   MoveToGroup)
from screens import PRIMARY_SCREEN, SECONDARY_SCREEN
from system import get_hostconfig
from themes import current_theme, dmenu_defaults

log = logging.getLogger('myqtile')
log.setLevel(logging.DEBUG)


def get_keys(mod, num_groups, num_monitors):
    log.debug(dmenu_defaults)
    is_laptop = get_hostconfig('laptop')
    group_split = (num_groups / 2, )
    multi_monitor = num_monitors > 1

    keys = [
        # Switch between windows in current stack pane
        (
            [mod], "k",
            lazy.layout.up().when('stack'),
            lazy.layout.up().when('max'),
            lazy.layout.up().when('tile'),
            lazy.layout.up().when('slice'),
            lazy.layout.previous().when('monadtall'),
            #lazy.layout.previous().when(when_floating=True)
        ),
        (
            [mod], "j",
            lazy.layout.down().when('stack'),
            lazy.layout.down().when('max'),
            lazy.layout.down().when('tile'),
            lazy.layout.down().when('slice'),
            lazy.layout.next().when('monadtall'),
            #lazy.layout.next().when(when_floating=True)
        ),

        #([mod], "k", lazy.layout.up()),
        #([mod], "j", lazy.layout.down()),
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
        ([mod, "shift"], "Left", lazy.window.move_floating(-5, 0, 0, 0)),
        ([mod, "shift"], "Right", lazy.window.move_floating(5, 0, 0, 0)),
        ([mod, "shift"], "Up", lazy.window.move_floating(0, -5, 0, 0)),
        ([mod, "shift"], "Down", lazy.window.move_floating(0, 5, 0, 0)),

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
        ([mod, 'control'], 'q', lazy.spawn('dmenu-session')),
        # Toggle between different layouts as defined below
        ([mod], "space",    lazy.nextlayout()),
        ([mod], "q",      lazy.window.kill()),
        # Key([mod, "control"], "r", lazy.restart()),
        ([mod, "control"], "r", lazy.function(check_restart)),
        ([mod], "Right", lazy.screen.nextgroup()),
        ([mod], "Left", lazy.screen.prevgroup()),
        ([], "F6",      lazy.function(SwitchGroup(
            "6", SECONDARY_SCREEN if is_laptop else PRIMARY_SCREEN))),

        ([mod], "m", lazy.group.setlayout('max')),
        ([mod], "t", lazy.group.setlayout('tile')),
        ([mod], "s", lazy.group.setlayout('stack')),
        ([mod], "x", lazy.group.setlayout('monadtall')),
        ([mod], "f", lazy.window.toggle_floating()),
        #([mod], "t", lazy.group.setlayout('xmonad-tall')),

        # APP LAUNCHERS
        #([mod], "r", lazy.spawncmd()),
        ([mod], "F2", lazy.spawn("dmenu_run %s" % dmenu_defaults)),
        ([mod], "F3", lazy.function(list_windows_group)),
        ([mod], "F5", lazy.function(list_windows)),
        ([mod], "r", lazy.spawncmd()),
        ([mod], "Return", lazy.spawn("st")),
        ([mod, "shift"], "b", lazy.spawn("conkeror")),
        ([mod, "shift"], "p", lazy.spawn("passmenu")),
        ([mod, "control"], "b", lazy.spawn("pybrowse")),
        ([mod, ], "e", lazy.spawn("conf")),
        ([mod, ], "Return", lazy.spawn("st")),
        ([mod, "shift"], "g", lazy.spawn("google-chrome-stable")),
        ([mod, "control"], "s", lazy.spawn("surf")),
        ([mod, "control"], "l", lazy.spawn("xscreensaver-command -lock")),
        #([], "3270_PrintScreen", lazy.spawn("ksnapshot")),
        ([mod, "shift"], "s", lazy.spawn("ksnapshot")),
        ([mod, "control"], "Escape", lazy.spawn("xkill")),
        ([mod, "shift"], "F2", lazy.spawn("dmenu_xclip %s" % dmenu_defaults)),
        ([], "XF86Launch1", lazy.function(
            RaiseWindowOrSpawn(
                wmname='tail', cmd='st -t tail -e sudo journalctl -xf',
                cmd_match="st -t tail", floating=True,
                toggle=True,
                static=[0, 100, 100, 1024, 200]))),
        # Switch groups
        ([], "F1", lazy.function(SwitchGroup("1"))),
        ([], "F2", lazy.function(SwitchGroup("2"))),

        ([], "Menu", lazy.function(SwitchToWindowGroup(
            'monitor', 'monitor', screen=PRIMARY_SCREEN,
            spawn=terminal('monitor')))),
        ([], "XF86Eject", lazy.function(SwitchToWindowGroup(
            'monitor', 'monitor', screen=PRIMARY_SCREEN,
            spawn=terminal('monitor')))),
        ([], "F10", lazy.function(SwitchToWindowGroup(
            'mail', 'mail', screen=PRIMARY_SCREEN, spawn=terminal('mail')))),
        ([], "F9", lazy.function(SwitchToWindowGroup(
            'comm', 'comm', screen=PRIMARY_SCREEN, spawn=terminal('comm')))),
        ([], "F11", lazy.function(SwitchToWindowGroup(
            'left', 'left', screen=SECONDARY_SCREEN, spawn=terminal('left')))),
        ([], "F12", lazy.function(SwitchToWindowGroup(
            'right', 'right', screen=PRIMARY_SCREEN, spawn=terminal('right')))),
    ]

    laptop_keys = [
        # laptop keys
        ([], "XF86MonBrightnessUp", lazy.spawn("sudo samctl.py -s up")),
        ([], "XF86MonBrightnessDown", lazy.spawn(
            "sudo samctl.py -s down")),
        ([], "XF86KbdBrightnessUp", lazy.spawn("sudo samctl.py -k up")),
        ([], "XF86KbdBrightnessDown", lazy.spawn(
            "sudo samctl.py -k down")),
        # Media controls
        ([], "XF86AudioMute", lazy.function(RaiseWindowOrSpawn(wmclass='Pavucontrol', cmd='pavucontrol'))),
        #([], "XF86AudioMute", lazy.spawn("pavucontrol")),
        ([], "XF86AudioLowerVolume", lazy.spawn("samctl.py -k up")),
        ([], "XF86AudioRaiseVolume", lazy.spawn("samctl.py -v down")),
        ([], "XF86WLAN", lazy.spawn(
            "nmcli con up id Xperia\ Z1\ Network --nowait")),
    ]
    if is_laptop:
        keys.extend(laptop_keys)

    for i in range(1, 11):
        keys.append(([mod], str(i)[-1], lazy.function(SwitchGroup(i))))
        keys.append(([mod, "shift"], str(i)[-1], lazy.function(MoveToGroup(i))))
    return [Key(*k) for k in keys]
