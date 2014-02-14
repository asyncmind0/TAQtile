from libqtile.config import Key, Click, Drag, Screen, Group, Match, Rule
from libqtile.command import lazy
from libqtile import layout, bar, widget
from extra import SwitchToWindowGroup, check_restart, terminal


def get_keys(mod):
    keys = [
        # Switch between windows in current stack pane
        Key([mod], "k", lazy.layout.down()),
        Key([mod], "j", lazy.layout.up()),
        # Move windows up or down in current stack
        Key([mod, "control"], "k", lazy.layout.shuffle_down()),
        Key([mod, "control"], "j", lazy.layout.shuffle_up()),

        # Switch window focus to other pane(s) of stack
        Key([mod], "space", lazy.layout.next()),

        # Swap panes of split stack
        Key([mod, "shift"], "space", lazy.layout.rotate()),

        # Toggle between split and unsplit sides of stack.
        # Split = all windows displayed
        # Unsplit = 1 window displayed, like Max layout, but still with
        # multiple stack panes
        Key([mod, "shift"], "Return", lazy.layout.toggle_split()),
        Key([mod], "Return", lazy.spawn("xterm")),
        Key(["shift", mod], "q", lazy.shutdown()),

        # Toggle between different layouts as defined below
        Key([mod], "Tab",    lazy.nextlayout()),
        Key([mod], "w",      lazy.window.kill()),

        # Key([mod, "control"], "r", lazy.restart()),
        Key([mod, "control"], "r", lazy.function(check_restart)),
        Key([mod], "r", lazy.spawncmd()),
        Key([], "F11", lazy.function(
            SwitchToWindowGroup("left", terminal("left"), 1))),
        Key([], "F12", lazy.function(
            SwitchToWindowGroup("right", terminal("right"), 0))),
    ]
    return keys