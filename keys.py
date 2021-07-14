import logging
from libqtile import extension
from libqtile.command import lazy
from libqtile.config import Key, Match, Rule
from extra import (
    SwitchToWindowGroup,
    ToggleApplication,
    check_restart,
    terminal_tmux,
    terminal,
    MoveToOtherScreenGroup,
    SwitchToScreenGroup,
    RaiseWindowOrSpawn,
    MoveToGroup,
    move_to_next_group,
    move_to_prev_group,
    autossh_term,
    show_mail,
    hide_show_bar,
)
from dmenu import (
    dmenu_org,
    list_bluetooth,
    list_calendars,
    dmenu_pushbullet,
)
from system import get_hostconfig, get_group_affinity, get_screen_affinity
from screens import PRIMARY_SCREEN, SECONDARY_SCREEN, TERTIARY_SCREEN
from system import get_hostconfig
from themes import current_theme, dmenu_cmd_args
from os.path import expanduser
from hooks import set_groups
from log import logger
import re
from subprocess import check_output
import six
import shlex
from extensions import Surf, DmenuRunRecent, BroTab, PassMenu, Inboxes
from clip import dmenu_xclip

re_vol = re.compile(r"\[(\d?\d?\d?)%\]")
re_touchpad = re.compile(r".*TouchpadOff\s*= 1", re.DOTALL)


def brightness_cmd(qtile, cmd):
    check_output(shlex.split(cmd))
    check_output(
        [
            "dunstify",
            "-t",
            "1000",
            "-r",
            "1999990",
            "Brightness: %s"
            % check_output(["xbacklight", "-get"]).decode().strip(),
        ]
    )


def get_current_volume():
    current_volume = 0
    mixer_out = check_output(["amixer", "sget", "Master"])
    if six.PY3:
        mixer_out = mixer_out.decode()
    if "[off]" in mixer_out:
        current_volume = "Muted"
    else:
        volgroups = re_vol.search(mixer_out)
        if volgroups:
            current_volume = int(volgroups.groups()[0])
        else:
            # this shouldn't happen
            current_volume = -1
    return current_volume


def volume_cmd(qtile, cmd):
    check_output(shlex.split(cmd))
    check_output(
        [
            "dunstify",
            "-t",
            "1000",
            "-r",
            "1999990",
            "Volume: %s" % get_current_volume(),
        ]
    )
    check_output(["pactl", "play-sample", "audio-volume-change"])


def volume_mute(qtile):
    check_output(["amixer", "-q", "sset", "Master", "toggle"])
    check_output(
        [
            "dunstify",
            "-t",
            "1000",
            "-r",
            "1999990",
            "Volume: %s" % get_current_volume(),
        ]
    )


def touchpad_toggle(qtile):
    touchpad_state = check_output(["synclient", "-l"])
    if six.PY3:
        touchpad_state = touchpad_state.decode()
    touchpad_state = bool(re_touchpad.search(touchpad_state))
    if touchpad_state:
        check_output(["synclient", "TouchpadOff=0"])
    else:
        check_output(["synclient", "TouchpadOff=1"])
    check_output(
        [
            "dunstify",
            "-t",
            "1000",
            "-r",
            "1999990",
            "Touch Pad %s" % ("On" if touchpad_state else "Off"),
        ]
    )


def notify_spawn(qtile, cmd):
    qtile.cmd_spawn(
        "sh -c 'notify-send %s;pactl play-sample audio-volume-change ;%s'" % cmd
    )


def get_keys(mod, num_groups, num_monitors):
    logger.debug(dmenu_cmd_args)
    is_laptop = get_hostconfig("laptop")

    keys = [
        # Switch between windows in current stack pane
        (
            [mod],
            "k",
            lazy.layout.up(),
            # lazy.layout.up().when('stack'),
            # lazy.layout.up().when('max'),
            ##lazy.layout.up().when('tile'),
            ##lazy.layout.up().when('slice'),
            ##lazy.layout.previous().when('monadtall'),
            # lazy.group.prev_window().when('floating'),
            # lazy.window.bring_to_front().when("floating"),
        ),
        (
            [mod],
            "j",
            lazy.layout.down(),
            # lazy.layout.down().when('stack'),
            # lazy.layout.down().when('max'),
            ##lazy.layout.down().when('tile'),
            ##lazy.layout.down().when('slice'),
            ##lazy.layout.next().when('monadtall'),
            # lazy.group.next_window().when('floating'),
            # lazy.window.bring_to_front().when("floating"),
        ),
        # ([mod], "k", lazy.layout.up()),
        # ([mod], "j", lazy.layout.down()),
        # Move windows up or down in current stack
        ([mod, "shift"], "k", lazy.layout.shuffle_up()),
        ([mod, "shift"], "j", lazy.layout.shuffle_down()),
        ([mod, "shift"], "h", lazy.layout.client_to_previous().when("stack")),
        ([mod, "shift"], "l", lazy.layout.client_to_next().when("stack")),
        ([mod], "h", lazy.group.prev_window()),
        ([mod], "l", lazy.group.next_window()),
        ([mod], "comma", lazy.layout.client_to_next()),
        ([mod], "period", lazy.layout.client_to_previous()),
        ([mod, "shift"], "comma", lazy.function(move_to_prev_group)),
        ([mod, "shift"], "period", lazy.function(move_to_next_group)),
        (
            [mod, "shift"],
            "space",
            lazy.layout.flip().when("monadtall"),
            lazy.layout.rotate().when("tile"),
        ),
        ([mod, "shift"], "Left", lazy.window.move_floating(-5, 0, 0, 0)),
        ([mod, "shift"], "Right", lazy.window.move_floating(5, 0, 0, 0)),
        ([mod, "shift"], "Up", lazy.window.move_floating(0, -5, 0, 0)),
        ([mod, "shift"], "Down", lazy.window.move_floating(0, 5, 0, 0)),
        (
            [mod, "shift", "control"],
            "Left",
            lazy.window.resize_floating(-5, 0, 0, 0),
        ),
        (
            [mod, "shift", "control"],
            "Right",
            lazy.window.resize_floating(5, 0, 0, 0),
        ),
        (
            [mod, "shift", "control"],
            "Up",
            lazy.window.resize_floating(0, -5, 0, 0),
        ),
        (
            [mod, "shift", "control"],
            "Down",
            lazy.window.resize_floating(0, 5, 0, 0),
        ),
        # Swap panes of split stack
        # toggle between windows just like in unity with 'alt+tab'
        (["mod1", "shift"], "Tab", lazy.layout.down()),
        (["mod1"], "Tab", lazy.layout.up()),
        (
            [mod, "shift"],
            "comma",
            lazy.function(MoveToOtherScreenGroup(prev=True)),
        ),
        (
            [mod, "shift"],
            "period",
            lazy.function(MoveToOtherScreenGroup(prev=False)),
        ),
        # Toggle between split and unsplit sides of stack.
        # Split = all windows displayed
        # Unsplit = 1 window displayed, like Max layout, but still with
        # multiple stack panes
        ([mod, "shift"], "Return", lazy.layout.toggle_split()),
        (["shift", mod], "q", lazy.shutdown()),
        ([mod, "control"], "q", lazy.spawn("dmenu-session")),
        # Toggle between different layouts as defined below
        # ([mod], "space",    lazy.nextlayout()),
        ([mod], "q", lazy.window.kill()),
        # Key([mod, "control"], "r", lazy.restart()),
        ([mod, "control"], "r", lazy.function(check_restart)),
        ([mod, "shift"], "r", lazy.function(set_groups)),
        ([mod, "shift"], "m", lazy.function(show_mail)),
        ([mod], "Right", lazy.screen.next_group()),
        ([mod], "Left", lazy.screen.prev_group()),
        ([mod], "m", lazy.group.setlayout("max")),
        ([mod], "t", lazy.group.setlayout("tile")),
        ([mod], "s", lazy.group.setlayout("stack")),
        ([mod], "x", lazy.group.setlayout("monadtall")),
        ([mod], "f", lazy.window.toggle_floating()),
        ([mod], "n", lazy.window.toggle_minimize()),
        # ([mod], "t", lazy.group.setlayout('xmonad-tall')),
        # APP LAUNCHERS
        # ([mod], "r", lazy.spawncmd()),
        # ([mod], "F2", lazy.spawn("dmenu-run-recent %s" % dmenu_cmd_args)),
        ([mod], "o", lazy.function(dmenu_org)),
        # ([mod], "f5", lazy.spawn('st -t {0} -e {0}'.format('ncmpcpp'))),
        ([mod], "r", lazy.spawncmd()),
        ([mod], "Return", lazy.spawn("st")),
        ([mod, "shift"], "b", lazy.spawn("conkeror")),
        # ([mod, "shift"], "b", lazy.spawn("google-chrome-stable")),
        ([mod, "shift"], "g", lazy.spawn("google-chrome-stable")),
        ([mod, "shift"], "p", lazy.run_extension(PassMenu(**current_theme))),
        ([mod, "control"], "p", lazy.function(dmenu_pushbullet)),
        ([mod, "control"], "b", lazy.spawn("pybrowse")),
        ([mod, "control"], "l", lazy.spawn(expanduser("~/.bin/lock"))),
        ([mod], "F1", lazy.spawn("sh -c 'sleep 5;xset dpms force off'")),
        # ([], "3270_PrintScreen", lazy.spawn("ksnapshot")),
        ([mod, "shift"], "c", lazy.spawn("flameshot gui")),
        ([mod, "shift"], "s", lazy.spawn("spectacle")),
        ([mod, "shift"], "m", lazy.spawn("kmag")),
        ([mod, "control"], "Escape", lazy.spawn("xkill")),
        # ([mod], "b", lazy.function(hide_show_bar)),
        ([mod], "b", lazy.hide_show_bar("bottom")),
        # (["control"], "Escape", lazy.spawn("ksysguard")),
        # ([mod, "shift"], "F2", lazy.function(dmenu_xclip, dmenu_cmd_args)),
        (["mod1", "control"], "v", lazy.function(dmenu_xclip, dmenu_cmd_args)),
        # (["mod1", "control"], "v", lazy.spawn("clipmenu")),
        # (["shift", mod], "v", lazy.function(dmenu_clip)),
        # ([], "XF86Launch1", lazy.function(
        #    RaiseWindowOrSpawn(
        #        wmname='tail', cmd='st -t tail -e sudo journalctl -xf',
        #        cmd_match="st -t tail", floating=True,
        #        toggle=True,
        #        static=[0, 100, 100, 1024, 200]))),
        (
            [mod],
            "e",
            lazy.function(
                SwitchToWindowGroup(
                    "krusader",
                    "krusader",
                    screen=SECONDARY_SCREEN,
                    spawn="krusader",
                )
            ),
        ),
        # Switch groups
        ([], "F1", lazy.function(SwitchToScreenGroup("browser"))),
        ([], "F2", lazy.function(SwitchToScreenGroup("emacs"))),
        ([], "F6", lazy.function(SwitchToScreenGroup("slack"))),
        ([mod], "F6", lazy.function(list_bluetooth)),
        (
            [],
            "F7",
            lazy.function(
                SwitchToScreenGroup("webcon", preferred_screen=SECONDARY_SCREEN)
            ),
        ),
        (
            [],
            "F10",
            lazy.run_extension(Inboxes(dmenu_ignorecase=True, **current_theme)),
        ),
        (
            [mod],
            "0",
            lazy.function(list_calendars),
        ),
        (
            ["control"],
            "Escape",
            lazy.function(
                SwitchToWindowGroup(
                    "comm1",
                    title="System Monitor",
                    screen=PRIMARY_SCREEN,
                    spawn="ksysguard",
                )
            ),
        ),
        ([mod], "space", lazy.run_extension(DmenuRunRecent(**current_theme))),
        (
            [mod],
            "w",
            lazy.run_extension(
                extension.WindowList(
                    dmenu_prompt="windows:",
                    dmenu_ignorecase=True,
                    dmenu_font=current_theme["font"],
                    **current_theme
                )
            ),
        ),
        (
            [mod, "shift"],
            "w",
            lazy.run_extension(
                extension.WindowList(
                    dmenu_prompt="windows:",
                    all_groups=False,
                    dmenu_ignorecase=True,
                    dmenu_font=current_theme["font"],
                    **current_theme
                )
            ),
        ),
    ]

    laptop_keys = [
        # laptop keys
        (
            [],
            "XF86MonBrightnessUp",
            lazy.function(brightness_cmd, get_hostconfig("brightness_up")),
        ),
        (
            [],
            "XF86MonBrightnessDown",
            lazy.function(brightness_cmd, get_hostconfig("brightness_down")),
        ),
        (
            [],
            "XF86KbdBrightnessUp",
            lazy.spawn(get_hostconfig("kbd_brightness_up")),
        ),
        (
            [],
            "XF86KbdBrightnessDown",
            lazy.spawn(get_hostconfig("kbd_brightness_down")),
        ),
        # Media controls
        ([], "XF86TouchpadToggle", lazy.function(touchpad_toggle)),
        (
            [],
            "XF86AudioLowerVolume",
            lazy.function(volume_cmd, get_hostconfig("volume_down")),
        ),
        (
            [],
            "XF86AudioRaiseVolume",
            lazy.function(volume_cmd, get_hostconfig("volume_up")),
        ),
        (
            [],
            "XF86LaunchB",
            lazy.function(
                RaiseWindowOrSpawn(wmclass="Pavucontrol", cmd="kmix")
            ),
        ),
        (
            [],
            "XF86Launch1",
            lazy.function(
                RaiseWindowOrSpawn(wmclass="Pavucontrol", cmd="pavucontrol")
            ),
        ),
        ([], "XF86AudioMute", lazy.function(volume_mute)),
        ([], "XF86AudioPlay", lazy.spawn("sp play")),
        ([], "XF86AudioPause", lazy.spawn("sp pause")),
        ([], "XF86AudioPrev", lazy.spawn("sp prev")),
        ([], "XF86AudioNext", lazy.spawn("sp next")),
        ([], "XF86WLAN", lazy.spawn(expanduser("~/.bin/mobilenet"))),
        ([mod], "u", lazy.group["scratch"].dropdown_toggle("st")),
        ([mod], "F3", lazy.group["scratch"].dropdown_toggle("htop")),
        # ([mod], "F11", lazy.group["scratch"].dropdown_toggle("pamixer")),
        (
            [mod],
            "g",
            lazy.run_extension(
                Surf(
                    dmenu_ignorecase=True,
                    item_format="* {window}",
                    **current_theme
                )
            ),
        ),
        (
            [mod],
            "F4",
            lazy.function(
                RaiseWindowOrSpawn(
                    wmname="htop",
                    cmd_match=terminal("htop", "htop"),
                    floating=True,
                    # static=(0, 0, 0, 1424, 500),
                    cmd=terminal("htop", "htop"),
                )
            ),
        ),
    ]

    keys.extend(laptop_keys)
    for i in range(1, 10):
        keys.append(([mod], str(i)[-1], lazy.function(SwitchToScreenGroup(i))))
        keys.append(([mod, "shift"], str(i)[-1], lazy.function(MoveToGroup(i))))
    return [Key(*k) for k in keys]
