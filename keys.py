import logging
from libqtile.command import lazy
from libqtile.config import Key, Match, Rule
from extra import (
    SwitchToWindowGroup, check_restart,
    terminal_tmux, terminal, MoveToOtherScreenGroup, SwitchToScreenGroup,
    RaiseWindowOrSpawn, MoveToGroup, move_to_next_group, move_to_prev_group,
    autossh_term, show_mail)
from dmenu import dmenu_run, list_windows, list_windows_group, dmenu_org
from screens import PRIMARY_SCREEN, SECONDARY_SCREEN
from system import get_hostconfig
from themes import current_theme, dmenu_defaults
from clipboard import dmenu_xclip
from passmenu import passmenu
from os.path import expanduser
from hooks import set_groups
from log import logger
import re


samctl = "sudo /home/steven/.bin/samctl.py"


def get_keys(mod, num_groups, num_monitors):
    logger.debug(dmenu_defaults)
    is_laptop = get_hostconfig('laptop')
    term1_key = get_hostconfig('term1_key')
    term2_key = get_hostconfig('term2_key')
    term3_key = get_hostconfig('term3_key')
    term4_key = get_hostconfig('term4_key')

    keys = [
        # Switch between windows in current stack pane
        (
            [mod], "k",
            lazy.layout.up().when('stack'),
            lazy.layout.up().when('max'),
            #lazy.layout.up().when('tile'),
            #lazy.layout.up().when('slice'),
            #lazy.layout.previous().when('monadtall'),
            lazy.group.prev_window().when('floating'),
            lazy.window.bring_to_front().when("floating"),
        ),
        (
            [mod], "j",
            #lazy.layout.next(),
            lazy.layout.down().when('stack'),
            lazy.layout.down().when('max'),
            #lazy.layout.down().when('tile'),
            #lazy.layout.down().when('slice'),
            #lazy.layout.next().when('monadtall'),
            lazy.group.next_window().when('floating'),
            lazy.window.bring_to_front().when("floating"),
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
        ([mod, "shift"], "m", lazy.function(show_mail)),
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
        ([mod], "o", lazy.function(dmenu_org)),
        #([mod], "F2", lazy.spawn("dmenu_run %s" % dmenu_defaults)),
        ([mod], "F3", lazy.function(list_windows_group)),
        #([mod], "f5", lazy.spawn('st -t {0} -e {0}'.format('ncmpcpp'))),
        ([mod], "r", lazy.spawncmd()),
        ([mod], "Return", lazy.spawn("st -t shrapnel")),
        ([mod, "shift"], "b", lazy.spawn("conkeror")),
        #([mod, "shift"], "b", lazy.spawn("google-chrome-stable")),
        ([mod, "shift"], "g", lazy.spawn("google-chrome-stable")),
        ([mod, "shift"], "p", lazy.function(passmenu, dmenu_defaults)),
        ([mod, "shift"], "c", lazy.spawn("spectacle")),
        ([mod, "control"], "b", lazy.spawn("pybrowse")),
        ([mod, "control"], "s", lazy.spawn("surf")),
        ([mod, "control"], "l", lazy.spawn("xscreensaver-command -lock")),
        ([mod], "F1", lazy.spawn(expanduser("~/.bin/blank"))),
        #([], "3270_PrintScreen", lazy.spawn("ksnapshot")),
        ([mod, "shift"], "s", lazy.spawn("spectacle")),
        ([mod, "shift"], "m", lazy.spawn("kmag")),
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
        ([], "F1", lazy.function(SwitchToScreenGroup("1"))),
        ([], "F2", lazy.function(SwitchToScreenGroup("2"))),

        #([], "Menu", lazy.function(SwitchToWindowGroup(
        #    'monitor', 'monitor', screen=PRIMARY_SCREEN,
        #    spawn=terminal_tmux('outer', 'monitor')))),
        #([], "XF86Eject", lazy.function(SwitchToWindowGroup(
        #    'monitor', 'monitor', screen=PRIMARY_SCREEN,
        #    spawn=terminal_tmux('outer', 'monitor')))),
        ([], "F6", lazy.function(SwitchToScreenGroup(
            "6", preferred_screen=SECONDARY_SCREEN))),
        ([], "F7", lazy.function(SwitchToScreenGroup(
            "7", preferred_screen=SECONDARY_SCREEN))),
        ([], "F9", lazy.function(SwitchToWindowGroup(
            'comm1', 'comm1', screen=PRIMARY_SCREEN,
            spawn=terminal_tmux('inner', 'comm1')))),
        (
            [],
            "F10",
            lazy.function(
                SwitchToWindowGroup(
                    'mail',
                    title=re.compile('Inbox .*$'),
                    screen=PRIMARY_SCREEN,
                    spawn=[
                        {
                            'cmd': 'google-chrome-stable --app="https://inbox.google.com/u/0/"',
                            'match': re.compile(r"^Inbox .* melit.stevenjoseph@gmail.com$"),
                        }, {
                            'cmd': 'google-chrome-stable --app="https://inbox.google.com/u/1/"',
                            'match': re.compile(r"^Inbox .* steven@streethawk.co$"),
                        }, {
                            'cmd': 'google-chrome-stable --app="https://inbox.google.com/u/2/"',
                            'match': re.compile(r"^Inbox .* stevenjose@gmail.com$"),
                        }, {
                            'cmd': 'google-chrome-stable --app="https://inbox.google.com/u/3/"',
                            'match': re.compile(r"^Inbox .* steven@stevenjoseph.in$"),
                        }
                    ]
                )
            )
        ),
        (
            [mod],
            "0",
            lazy.function(
                SwitchToWindowGroup(
                    'cal',
                    title=re.compile('.* Calendar .*$'),
                    screen=PRIMARY_SCREEN,
                    spawn=[
                        {
                            "cmd": 'google-chrome-stable --app="https://calendar.google.com/calendar/b/1/"',
                            "match": re.compile(r'StreetHawk - Calendar .*$'),
                        },
                        {
                            "cmd": 'google-chrome-stable --app="https://calendar.google.com/calendar/b/0/"',
                            "match": re.compile(r'Google Calendar .*$'),
                        },
                    ]
                )
            )
        ),
        (
            [],
            term1_key,
            lazy.function(
                SwitchToWindowGroup(
                    'term1',
                    title='left',
                    screen=PRIMARY_SCREEN,
                    spawn=terminal_tmux(
                        'outer', 'left'
                        )

                    )
                )
        ),
        (
            [],
            term2_key,
            lazy.function(
                SwitchToWindowGroup(
                    'term2',
                    title='right',
                    screen=SECONDARY_SCREEN,
                    spawn=terminal_tmux(
                        'outer', 'right'
                        )
                    )
                )
        ),
        (
            [mod],
            term1_key,
            lazy.function(
                SwitchToWindowGroup(
                    'term1',
                    title='shawk_left',
                    screen=PRIMARY_SCREEN,
                    spawn=autossh_term(
                        title="shawk_left",
                        host="salt.streethawk.com",
                        session="left"
                        )
                    )
                )
        ),
        (
            [mod],
            term2_key,
            lazy.function(
                SwitchToWindowGroup(
                    'term2', title='shawk_right', screen=SECONDARY_SCREEN,
                    spawn=autossh_term(
                        title="shawk_right",
                        host="salt.streethawk.com",
                        session="right"
                        )
                    )
                )
        ),
        (
            [mod],
            term3_key,
            lazy.function(
                SwitchToWindowGroup(
                    'azure_left',
                    title='azure_left',
                    screen=PRIMARY_SCREEN,
                    spawn=autossh_term(
                        title="azure_left",
                        host="salt-streethawk.cloudapp.net",
                        session="left"
                        )
                    )
                )
        ),
        (
            [mod],
            term4_key,
            lazy.function(
                SwitchToWindowGroup(
                    'azure_right',
                    title='azure_right',
                    screen=SECONDARY_SCREEN,
                    spawn=autossh_term(
                        title="azure_right",
                        host="salt-streethawk.cloudapp.net",
                        session="right"
                    )
                )
            )
        ),
        (
            [mod],
            'F8',
            lazy.function(
                SwitchToWindowGroup(
                    'staging',
                    title='staging',
                    screen=PRIMARY_SCREEN,
                    spawn=autossh_term(
                            title="staging",
                            host="staging.streethawk.com",
                            session="right"
                        )
                    )
                )
        ),
        #(
        #    [mod, "shift"],
        #    term1_key,
        #    lazy.function(
        #        SwitchToWindowGroup(
        #            'term1', 'iress2_right', screen=PRIMARY_SCREEN,
        #            spawn=autossh_term(
        #                title="prod_right",
        #                port=9008,
        #            )
        #        )
        #    )
        #),
        #(
        #    [mod, "shift"],
        #    term2_key,
        #    lazy.function(
        #        SwitchToWindowGroup(
        #            'term2', 'iress2_left', screen=SECONDARY_SCREEN,
        #            spawn=autossh_term(
        #                title="prod_left",
        #                host="api.streethawk.com",
        #                )
        #            )
        #        )
        #),
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
        ([mod], "F5", lazy.function(list_windows)),
        ([mod], "F4", lazy.function(SwitchToWindowGroup(
            'htop', 'htop', screen=SECONDARY_SCREEN,
            spawn=terminal('htop', 'htop')))),
        #([mod], "F5", lazy.function(RaiseWindowOrSpawn(
        #    wmname='ncmpcpp',
        #    cmd='st -t {0} -e {0}'.format('ncmpcpp'),
        #    toggle=True,
        #    cmd_match="st -t ncmpcpp", floating=True))),
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

    for i in range(1, 10):
        keys.append(([mod], str(i)[-1], lazy.function(SwitchToScreenGroup(i))))
        keys.append(([mod, "shift"], str(i)[-1], lazy.function(MoveToGroup(i))))
    return [Key(*k) for k in keys]
