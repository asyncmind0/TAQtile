import re
import shlex
from os.path import expanduser
from subprocess import check_output

from libqtile import extension
from libqtile.command import lazy
from libqtile.config import Key as QKey

from taqtile.clip import dmenu_xclip
from taqtile.dmenu import (
    dmenu_show,
    dmenu_org,
    list_bluetooth,
    dmenu_pushbullet,
    dmenu_kubectl,
    switch_pulse_outputs,
    switch_pulse_inputs,
    set_volume,
)
from taqtile.extensions import (
    Surf,
    DmenuRunRecent,
    PassMenu,
    Inboxes,
    Calendars,
    BringWindowToGroup,
    SessionActions,
    KillWindows,
    WindowList,
)
from taqtile.extra import (
    SwitchToWindowGroup,
    check_restart,
    terminal,
    MoveToOtherScreenGroup,
    SwitchToScreenGroup,
    RaiseWindowOrSpawn,
    MoveToGroup,
    move_to_next_group,
    move_to_prev_group,
    show_mail,
    float_to_front,
)
from taqtile.hooks import set_groups
from taqtile.log import logger
from taqtile.screens import PRIMARY_SCREEN, SECONDARY_SCREEN
from taqtile.system import get_hostconfig, show_process_stats
from taqtile.themes import current_theme, dmenu_cmd_args
from taqtile.sounds import play_effect, change_sink_volume, volume_mute
from libqtile import hook
from taqtile.utils import send_notification
from taqtile.popups.powermenu import show_power_menu
from taqtile.popups.keyboard import show_keyboard


re_vol = re.compile(r"\[(\d?\d?\d?)%\]")
re_touchpad = re.compile(r".*TouchpadOff\s*= 1", re.DOTALL)
win_list = []


def stick_win(qtile):
    global win_list
    win_list.append(qtile.current_window)


def unstick_win(qtile):
    global win_list
    if qtile.current_window in win_list:
        try:
            win_list.remove(qtile.current_window)
        except ValueError:
            pass

@hook.subscribe.client_focus
def client_focus(client):
    for w in win_list:
        try:
            w.bring_to_front()
        except ValueError:
            pass
@hook.subscribe.setgroup
def move_win():
    from libqtile import qtile

    for w in win_list:
        try:
            w.togroup(qtile.current_group.name)
            w.focus()
        except ValueError:
            pass


class Key(QKey):
    def __init__(
        self,
        modifiers: list[str],
        key: str,
        command,
        desc: str = "",
    ) -> None:
        super().__init__(modifiers, key, command, desc=desc)


def brightness_cmd(qtile, cmd):
    check_output(shlex.split(cmd))
    send_notification(
        "Brighness",
        check_output(["xbacklight", "-get"]).decode().strip(),
    )


def switch_window(qtile, cmd):
    getattr(qtile.current_layout, cmd)()
    send_notification(
        "Window",
        qtile.current_window.name,
    )


def touchpad_toggle(qtile):
    touchpad_state = check_output(["synclient", "-l"]).decode()
    touchpad_state = bool(re_touchpad.search(touchpad_state))
    if touchpad_state:
        check_output(["synclient", "TouchpadOff=0"])
    else:
        check_output(["synclient", "TouchpadOff=1"])
    send_notification(
        "Touch Pad",
        ("On" if touchpad_state else "Off"),
    )


def list_keys(qtile, *args):
    from config import keys

    selected = dmenu_show(
        "Keybindings:",
        [f"{' '.join(x.modifiers)} {x.key} {x.desc}" for x in keys],
    )
    logger.info("selected: {selected}")


def get_keys(mod, num_groups, num_monitors):
    logger.debug(dmenu_cmd_args)
    is_laptop = get_hostconfig("laptop")

    keys = [
        # Switch between windows in current stack pane
        (
            [mod],
            "k",
            lazy.layout.up(),
            "Layout Up"
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
            "Layout Down"
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
        ([mod, "shift"], "k", lazy.layout.shuffle_up(), "Shuffle Up"),
        ([mod], "Up", lazy.layout.previous()),
        ([mod, "shift"], "j", lazy.layout.shuffle_down()),
        ([mod], "Down", lazy.layout.next()),
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
        #(["shift", mod], "q", lazy.shutdown()),
        (
            [mod, "control"],
            "q",
            lazy.run_extension(SessionActions(**current_theme)),
        ),
        # (["control"], "space", lazy.widget["notify"].clear()),
        (["control"], "space", lazy.spawn("dunstctl close")),
        (["control"], "grave", lazy.spawn("dunstctl history-pop")),
        # (["control"], "grave", lazy.widget["notify"].prev()),
        # (["control", "shift"], "grave", lazy.widget["notify"].next()),
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
        (
            [mod],
            "Return",
            lazy.spawn(terminal("shrapnel", window_class="shrapnel")),
        ),
        ([mod, "shift"], "b", lazy.spawn("conkeror")),
        # ([mod, "shift"], "b", lazy.spawn("google-chrome-stable")),
        (
            [mod, "control"],
            "g",
            lazy.run_extension(KillWindows(**current_theme)),
        ),
        ([mod], "v", lazy.function(set_volume)),
        ([mod], "p", lazy.function(switch_pulse_outputs)),
        ([mod], "i", lazy.function(switch_pulse_inputs)),
        ([mod, "shift"], "p", lazy.run_extension(PassMenu(**current_theme))),
        ([mod, "control"], "p", lazy.function(dmenu_pushbullet)),
        ([mod, "control"], "b", lazy.spawn("pybrowse")),
        ([mod, "control"], "l", lazy.spawn(expanduser("~/.bin/lock"))),
        # ([mod], "F1", lazy.spawn("sh -c 'sleep 5;xset dpms force off'")),
        # ([], "3270_PrintScreen", lazy.spawn("ksnapshot")),
        ([mod, "shift"], "c", lazy.spawn("flameshot gui")),
        ([mod, "shift"], "s", lazy.spawn("spectacle")),
        ([mod, "shift"], "m", lazy.spawn("kmag")),
        ([mod, "control"], "Escape", lazy.spawn("xkill")),
        # (["control"], "Escape", lazy.spawn("ksysguard")),
        ([mod, "shift"], "h", lazy.function(list_keys, [])),
        # ([mod], "b", lazy.function(hide_show_bar)),
        ([mod], "b", lazy.hide_show_bar("bottom")),
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
            lazy.spawn("dolphin")
            # lazy.function(
            #    SwitchToWindowGroup(
            #        "krusader",
            #        "krusader",
            #        screen=SECONDARY_SCREEN,
            #        spawn="krusader",
            #    )
            # ),
        ),
        # Switch groups
        ([], "F1", lazy.function(SwitchToScreenGroup("work"))),
        ([], "F2", lazy.function(SwitchToScreenGroup("home"))),
        ([], "F3", lazy.function(SwitchToScreenGroup("audio"))),
        ([], "F4", lazy.function(SwitchToScreenGroup("crypto"))),
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
            lazy.run_extension(
                Calendars(dmenu_ignorecase=True, **current_theme)
            ),
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
            ["mod1"],
            "XF86AudioLowerVolume",
            lazy.function(switch_window, "down"),
            "Layout Down",
        ),
        (
            ["mod1"],
            "XF86AudioRaiseVolume",
            lazy.function(switch_window, "up"),
            "Layout Up",
        ),
        (
            [mod],
            "Escape",
            lazy.run_extension(
                WindowList(
                    item_format="{window}",
                    dmenu_prompt="windows:",
                    # all_groups=False,
                    dmenu_ignorecase=True,
                    dmenu_font=current_theme["font"],
                    **current_theme,
                )
            ),
        ),
        (
            [mod],
            "Menu",
            lazy.run_extension(
                WindowList(
                    item_format="{window}",
                    all_groups=False,
                    dmenu_prompt="windows:",
                    dmenu_ignorecase=True,
                    dmenu_font=current_theme["font"],
                    **current_theme,
                )
            ),
        ),
        ([mod, "shift"], "k", lazy.function(dmenu_kubectl)),
        ([mod, "shift"], "f", lazy.function(float_to_front)),
        ([mod], "o", lazy.function(stick_win), "stick win"),
        ([mod, "shift"], "o", lazy.function(unstick_win), "unstick win"),
        ([mod, "shift"], "e", lazy.spawn("dmenumoji")),
        ([mod, "shift"], "q", lazy.function(show_power_menu)),
        ([mod, "shift"], "k", lazy.function(show_keyboard))
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
            lazy.function(change_sink_volume, -0.01),
        ),
        ([mod], "XF86AudioLowerVolume", lazy.function(set_volume)),
        ([mod], "XF86AudioRaiseVolume", lazy.function(set_volume)),
        (
            [],
            "XF86AudioRaiseVolume",
            lazy.function(change_sink_volume, 0.01),
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
        (
            [mod],
            "XF86AudioMute",
            lazy.spawn(
                "dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.PlayPause"
            ),
        ),
        ([mod, "shift"], "d", lazy.function(show_process_stats)),
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
                    **current_theme,
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
