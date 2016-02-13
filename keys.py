import logging
from libqtile.command import lazy
from libqtile.config import Key, Match, Rule
from extra import (
    SwitchToWindowGroup, check_restart,
    terminal_tmux, terminal, MoveToOtherScreenGroup, SwitchGroup,
    RaiseWindowOrSpawn, MoveToGroup, move_to_next_group, move_to_prev_group)
from dmenu import dmenu_run, list_windows, list_windows_group
from screens import PRIMARY_SCREEN, SECONDARY_SCREEN
from system import get_hostconfig
from themes import current_theme, dmenu_defaults
from clipboard import dmenu_xclip
from passmenu import passmenu
from os.path import expanduser
from hooks import set_groups

log = logging.getLogger('myqtile')
log.setLevel(logging.DEBUG)

cmd_autossh_iress = (
    "st -t iress{2}_{0} -e /home/steven/.local/bin/autossh.py localhost:330{1} outer {0}"
)
samctl = "sudo /home/steven/.bin/samctl.py"


def get_keys(mod, num_groups, num_monitors):
    log.debug(dmenu_defaults)
    is_laptop = get_hostconfig('laptop')
    term1_key = get_hostconfig('term1_key')
    term2_key = get_hostconfig('term2_key')

    keys = [
        # Switch between windows in current stack pane
        (
            [mod], "k",
            lazy.layout.up().when('stack'),
            lazy.layout.up().when('max'),
            lazy.layout.up().when('tile'),
            lazy.layout.up().when('slice'),
            lazy.layout.previous().when('monadtall'),
            lazy.group.prev_window().when("floating"),
        ),
        (
            [mod], "j",
            #lazy.layout.next(),
            lazy.layout.down().when('stack'),
            lazy.layout.down().when('max'),
            lazy.layout.down().when('tile'),
            lazy.layout.down().when('slice'),
            lazy.layout.next().when('monadtall'),
            lazy.group.next_window().when("floating"),
        ),

        #([mod], "k", lazy.layout.up()),
        #([mod], "j", lazy.layout.down()),
        # Move windows up or down in current stack
        ([mod, "shift"], "k", lazy.layout.shuffle_up()),
        ([mod, "shift"], "j", lazy.layout.shuffle_down()),
        ([mod, "shift"], "h", lazy.layout.client_to_previous().when("stack")),
        ([mod, "shift"], "l", lazy.layout.client_to_next().when("stack")),

        ([mod], "h",
         lazy.group.prev_window()),
        ([mod], "l",
         lazy.group.next_window()),

        ([mod], "comma", lazy.layout.client_to_next()),
        ([mod], "period", lazy.layout.client_to_previous()),

        ([mod, "shift"], "comma", lazy.function(move_to_prev_group)),
        ([mod, "shift"], "period", lazy.function(move_to_next_group)),

        ([mod, "shift"], "space", lazy.layout.flip().when('monadtall'),
         lazy.layout.rotate().when('tile')),
        ([mod, "shift"], "Left", lazy.window.move_floating(-5, 0, 0, 0)),
        ([mod, "shift"], "Right", lazy.window.move_floating(5, 0, 0, 0)),
        ([mod, "shift"], "Up", lazy.window.move_floating(0, -5, 0, 0)),
        ([mod, "shift"], "Down", lazy.window.move_floating(0, 5, 0, 0)),
        ([mod, "shift", "control"],
         "Left", lazy.window.resize_floating(-5, 0, 0, 0)),
        ([mod, "shift", "control"],
         "Right", lazy.window.resize_floating(5, 0, 0, 0)),
        ([mod, "shift", "control"],
         "Up", lazy.window.resize_floating(0, -5, 0, 0)),
        ([mod, "shift", "control"],
         "Down", lazy.window.resize_floating(0, 5, 0, 0)),

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
        ([mod, "shift"], "r", lazy.function(set_groups)),
        ([mod], "Right", lazy.screen.next_group()),
        ([mod], "Left", lazy.screen.prev_group()),

        ([mod], "m", lazy.group.setlayout('max')),
        ([mod], "t", lazy.group.setlayout('tile')),
        ([mod], "s", lazy.group.setlayout('stack')),
        ([mod], "x", lazy.group.setlayout('monadtall')),
        ([mod], "f", lazy.window.toggle_floating()),
        ([mod], "n", lazy.window.toggle_minimize()),
        #([mod], "t", lazy.group.setlayout('xmonad-tall')),

        # APP LAUNCHERS
        #([mod], "r", lazy.spawncmd()),
        ([mod], "F2", lazy.function(dmenu_run)),
        #([mod], "F2", lazy.spawn("dmenu-run-recent %s" % dmenu_defaults)),
        ([mod], "o", lazy.spawn("orgcapture.py")),
        #([mod], "F2", lazy.spawn("dmenu_run %s" % dmenu_defaults)),
        ([mod], "F3", lazy.function(list_windows_group)),
        ([mod], "F4", lazy.function(list_windows)),
        #([mod], "F5", lazy.spawn('st -t {0} -e {0}'.format('ncmpcpp'))),
        ([mod], "r", lazy.spawncmd()),
        ([mod], "Return", lazy.spawn("st -t shrapnel")),
        ([mod, "shift"], "b", lazy.spawn("conkeror")),
        #([mod, "shift"], "b", lazy.spawn("google-chrome-stable")),
        ([mod, "shift"], "g", lazy.spawn("google-chrome-stable")),
        ([mod, "shift"], "p", lazy.function(passmenu, dmenu_defaults)),
        ([mod, "control"], "b", lazy.spawn("pybrowse")),
        ([mod, "control"], "s", lazy.spawn("surf")),
        ([mod, "control"], "l", lazy.spawn("xscreensaver-command -lock")),
        ([mod], "F1", lazy.spawn(expanduser("~/.bin/blank"))),
        #([], "3270_PrintScreen", lazy.spawn("ksnapshot")),
        ([mod, "shift"], "s", lazy.spawn("ksnapshot")),
        ([mod, "control"], "Escape", lazy.spawn("xkill")),
        ([mod, "shift"], "F2", lazy.function(dmenu_xclip, dmenu_defaults)),
        ([mod, "control"], "v", lazy.function(dmenu_xclip, dmenu_defaults)),
        #([], "XF86Launch1", lazy.function(
        #    RaiseWindowOrSpawn(
        #        wmname='tail', cmd='st -t tail -e sudo journalctl -xf',
        #        cmd_match="st -t tail", floating=True,
        #        toggle=True,
        #        static=[0, 100, 100, 1024, 200]))),
        ([mod], "e", lazy.function(SwitchToWindowGroup(
            'krusader', 'krusader', screen=SECONDARY_SCREEN,
            spawn="krusader"))),
        # Switch groups
        ([], "F1", lazy.function(SwitchGroup("1"))),
        ([], "F2", lazy.function(SwitchGroup("2"))),

        #([], "Menu", lazy.function(SwitchToWindowGroup(
        #    'monitor', 'monitor', screen=PRIMARY_SCREEN,
        #    spawn=terminal_tmux('outer', 'monitor')))),
        #([], "XF86Eject", lazy.function(SwitchToWindowGroup(
        #    'monitor', 'monitor', screen=PRIMARY_SCREEN,
        #    spawn=terminal_tmux('outer', 'monitor')))),
        #([], "F10", lazy.function(SwitchGroup("mail"))),
        ([], "F10", lazy.function(SwitchToWindowGroup(
            'mail', 'mail', screen=SECONDARY_SCREEN,
            spawn=terminal_tmux('inner', 'mail')))),
        ([], "F6", lazy.function(SwitchGroup(
            "comm2", preferred_screen=SECONDARY_SCREEN))),
        ([], "F9", lazy.function(SwitchToWindowGroup(
            'comm1', 'comm1', screen=PRIMARY_SCREEN,
            spawn=terminal_tmux('inner', 'comm1')))),
        ([], term1_key, lazy.function(SwitchToWindowGroup(
            'term1', 'left', screen=PRIMARY_SCREEN,
            spawn=terminal_tmux('outer', 'left')))),
        ([], term2_key, lazy.function(SwitchToWindowGroup(
            'term2', 'right', screen=SECONDARY_SCREEN,
            spawn=terminal_tmux('outer', 'right')))),
        ([mod], term1_key, lazy.function(SwitchToWindowGroup(
            'term1', 'iress_right', screen=PRIMARY_SCREEN,
            spawn=cmd_autossh_iress.format("right", "7", "")))),
        ([mod], term2_key, lazy.function(SwitchToWindowGroup(
            'term2', 'iress_left', screen=SECONDARY_SCREEN,
            spawn=cmd_autossh_iress.format("left", "7", "")))),
        ([mod, "shift"], term1_key, lazy.function(SwitchToWindowGroup(
            'term1', 'iress2_right', screen=PRIMARY_SCREEN,
            spawn=cmd_autossh_iress.format("right", "8", "2")))),
        ([mod, "shift"], term2_key, lazy.function(SwitchToWindowGroup(
            'term2', 'iress2_left', screen=SECONDARY_SCREEN,
            spawn=cmd_autossh_iress.format("left", "8", "2")))),
    ]

    laptop_keys = [
        # laptop keys
        ([], "XF86MonBrightnessUp", lazy.spawn("%s -s up" % samctl)),
        ([], "XF86MonBrightnessDown", lazy.spawn("%s -s down" % samctl)),
        ([], "XF86KbdBrightnessUp", lazy.spawn("%s -k up" % samctl)),
        ([], "XF86KbdBrightnessDown", lazy.spawn("%s -k down" % samctl)),
        # Media controls
        ([], "XF86LaunchB", lazy.function(RaiseWindowOrSpawn(
            wmclass='Pavucontrol', cmd='pavucontrol'))),
        ([], "XF86Launch1", lazy.function(RaiseWindowOrSpawn(
            wmclass='Pavucontrol', cmd='pavucontrol'))),
        # ([], "XF86AudioMute", lazy.spawn("pavucontrol")),
        #([], "XF86AudioLowerVolume", lazy.spawn("samctl.py -v down")),
        #([], "XF86AudioRaiseVolume", lazy.spawn("samctl.py -v up")),
        ([], "XF86AudioPlay", lazy.spawn("mpc toggle")),
        ([], "XF86AudioPause", lazy.spawn("mpc toggle")),
        ([], "XF86AudioPrev", lazy.spawn("mpc prev")),
        ([], "XF86AudioNext", lazy.spawn("mpc next")),
        ([], "XF86WLAN", lazy.spawn(
            expanduser("~/.bin/mobilenet"))),
        ([mod], "F5", lazy.function(RaiseWindowOrSpawn(
            wmname='ncmpcpp',
            cmd='st -t {0} -e {0}'.format('ncmpcpp'),
            toggle=True,
            cmd_match="st -t ncmpcpp", floating=True))),
    ]

    desktop_keys = [
        #([], "XF86Launch9", lazy.function(SwitchToWindowGroup(
        #    'remote_term1', 'remote_term1', screen=SECONDARY_SCREEN,
        #    spawn=terminal('remote_term1')))),
        #([], "F19", lazy.function(SwitchToWindowGroup(
        #    'remote_term2', 'remote_term2', screen=PRIMARY_SCREEN,
        #    spawn=terminal('remote_term2')))),
        ([], "KP_Begin", lazy.function(SwitchToWindowGroup(
            'htop', 'htop', screen=SECONDARY_SCREEN,
            spawn=terminal('htop', 'htop')))),
        ([], "KP_Left", lazy.function(SwitchToWindowGroup(
            'log', 'log', screen=SECONDARY_SCREEN,
            spawn=terminal('log', 'sudo journalctl -xf')))),
        ([], "KP_Right", lazy.function(SwitchToWindowGroup(
            'ulog', 'ulog', screen=SECONDARY_SCREEN,
            spawn=terminal('ulog', 'journalctl --user -xf')))),
        ([mod], "F5", lazy.spawn('/home/steven/.bin/rdp_dfs')),
    ]
    if is_laptop:
        keys.extend(laptop_keys)
    else:
        keys.extend(desktop_keys)

    for i in range(1, 11):
        keys.append(([mod], str(i)[-1], lazy.function(SwitchGroup(i))))
        keys.append(([mod, "shift"], str(i)[-1], lazy.function(MoveToGroup(i))))
    return [Key(*k) for k in keys]
