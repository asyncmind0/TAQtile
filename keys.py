import logging
from libqtile.command import lazy
from libqtile.config import Key
from extra import (SwitchToWindowGroup, check_restart,
                   terminal, MoveToOtherScreenGroup, SwitchGroup,
                   RaiseWindowOrSpawn, list_windows)
from screens import PRIMARY_SCREEN, SECONDARY_SCREEN
from system import get_hostconfig
from themes import current_theme, dmenu_defaults


def get_keys(mod, groups, dgroups_app_rules):
    #dmenu_defaults = dmenu_defaults.replace('#', '#')
    logging.debug(dmenu_defaults)
    is_laptop = get_hostconfig('laptop')
    left_termkey = get_hostconfig('left_termkey')
    right_termkey = get_hostconfig('right_termkey')
    left_remote_termkey = get_hostconfig('left_remote_termkey')
    right_remote_termkey = get_hostconfig('right_remote_termkey')
    monitor_key = get_hostconfig('monitor_key')
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
        ([mod], "F3", lazy.function(list_windows)),
        ([mod], "r", lazy.spawncmd()),
        ([mod], "Return", lazy.spawn("st")),
        ([mod, "shift"], "b", lazy.spawn("conkeror")),
        ([mod, "shift"], "p", lazy.spawn("passmenu")),
        ([mod, "shift"], "g", lazy.spawn("google-chrome-stable")),
        ([mod, "control"], "s", lazy.spawn("surf")),
        ([mod, "control"], "l", lazy.spawn("xscreensaver-command -lock")),
        #([], "3270_PrintScreen", lazy.spawn("ksnapshot")),
        ([mod, "shift"], "s", lazy.spawn("ksnapshot")),
        ([mod, "control"], "Escape", lazy.spawn("xkill")),
        ([mod, "shift"], "F2", lazy.spawn("dmenu_xclip %s" % dmenu_defaults)),
        
        # Switch groups
        ([], "F1", lazy.function(SwitchGroup("1"))),
        ([], "F2", lazy.function(SwitchGroup("2"))),
        #([], "F10", lazy.function(SwitchGroup("4", 0))),
        ([], "F10", lazy.function(
            SwitchToWindowGroup(
                groups, "mail", title=[".*mail.*"], cmd="kmail",
                wm_class=["kmail"], screen=PRIMARY_SCREEN,
                dynamic_groups_rules=dgroups_app_rules))),
        ([], "F9", lazy.function(
            SwitchToWindowGroup(
                groups, "comm", title=[".*comm.*"], cmd=terminal("comm"),
                wm_class=["InputOutput"], screen=PRIMARY_SCREEN,
                dynamic_groups_rules=dgroups_app_rules))),

        (left_termkey[0], left_termkey[1], lazy.function(
            SwitchToWindowGroup(
                groups, "left", title=[".*left.*"], cmd=terminal("left"),
                wm_class=["InputOutput"], screen=PRIMARY_SCREEN,
                dynamic_groups_rules=dgroups_app_rules))),

        (right_termkey[0], right_termkey[1], lazy.function(
            SwitchToWindowGroup(
                groups, "right", cmd=terminal("right"), title=[".*right.*"],
                wm_class=["InputOutput"], screen=SECONDARY_SCREEN,
                dynamic_groups_rules=dgroups_app_rules))),

        (left_remote_termkey[0], left_remote_termkey[1], lazy.function(
            SwitchToWindowGroup(
                groups, "remote_left", cmd="st -t remote_left ",
                screen=PRIMARY_SCREEN, title=[".*remote_left.*"],
                wm_class=["InputOutput"],
                dynamic_groups_rules=dgroups_app_rules))),

        (right_remote_termkey[0], right_remote_termkey[1], lazy.function(
            SwitchToWindowGroup(
                groups, "remote_right", cmd="st -t remote_right ",
                screen=SECONDARY_SCREEN, title=[".*remote_right.*"],
                wm_class=["InputOutput"],
                dynamic_groups_rules=dgroups_app_rules))),

        (monitor_key[0], monitor_key[1], lazy.function(
            SwitchToWindowGroup(
                groups, "monitor", cmd=terminal("monitor"),
                title=[".*monitor.*"], screen=SECONDARY_SCREEN,
                wm_class=["InputOutput"],
                dynamic_groups_rules=dgroups_app_rules))),
        ([], "XF86LaunchA", lazy.function(
            RaiseWindowOrSpawn(
                wmname='tail', cmd='st -t tail -e sudo journalctl -xf',
                cmd_match="st -t tail", floating=True,
                toggle=True,
                static=[0, 100, 100, 500, 200]))),
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
    return [Key(*k) for k in keys]
