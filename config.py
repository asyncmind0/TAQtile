# TODO handle MultiScreenGroupBox clicks and events
import logging
from os.path import expanduser

from libqtile import layout
from libqtile.command import lazy
from libqtile.config import Drag, Match

from taqtile.extra import Terminal, terminal
from taqtile.groups import generate_groups, get_dgroups
from taqtile.keys import get_keys
from taqtile.screens import (
    get_screens,
    PRIMARY_SCREEN,
    SECONDARY_SCREEN,
    TERTIARY_SCREEN,
)
from taqtile.system import get_num_monitors
from taqtile.themes import current_theme
from taqtile.layouts import Max


log_file_path = expanduser("~/.local/share/qtile/qtile.taqtile.log")
handler = logging.FileHandler(log_file_path)
formatter = logging.Formatter(
    "%(asctime)s %(levelname)s [%(name)s] %(message)s"
)
handler.setFormatter(formatter)

logger = logging.getLogger("taqtile")

logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
logger.info("Logger initialized")

mod = "mod4"
num_monitors = get_num_monitors()

layouts = [
    Max(**current_theme),
    layout.Stack(**current_theme),
    # layout.xmonad.MonadTall(ratio=0.50, **current_theme),
    # layout.Tile(**current_theme),
    # layout.Zoomy(**current_theme),
    # layout.TreeTab(),
    # a layout just for gimp
    # layout.Slice(
    #    "term1",
    #    192,
    #    name="gimp",
    #    role="gimp-toolbox",
    #    fallback=layout.Slice(
    #        "right",
    #        256,
    #        role="gimp-dock",
    #        fallback=layout.Stack(num_stacks=1, **border_args),
    #    ),
    # ),
]


# This allows you to drag windows around with the mouse if you want.
mouse = [
    Drag(
        [mod],
        "Button1",
        lazy.window.set_position_floating(),
        start=lazy.window.get_position(),
    ),
    Drag(
        [mod],
        "Button3",
        lazy.window.set_size_floating(),
        start=lazy.window.get_size(),
    ),
    # Click([mod], "Button2", lazy.window.bring_to_front())
]

float_windows = [
    "buddy_list",
]
follow_mouse_focus = False  # pylint: noqa, flake8: noqa
bring_front_click = True
cursor_warp = False
auto_fullscreen = True
widget_defaults = current_theme
dgroups_app_rules = get_dgroups()
num_groups = (num_monitors) * 10

groups = generate_groups(num_groups, layouts)
keys = get_keys(mod, num_groups, num_monitors)


Terminal(
    "term0",
    "F11",
    groups=groups,
    keys=keys,
    dgroups=dgroups_app_rules,
    screen=PRIMARY_SCREEN,
)

Terminal(
    "term1",
    "F12",
    groups=groups,
    keys=keys,
    dgroups=dgroups_app_rules,
    screen=SECONDARY_SCREEN,
)

Terminal(
    "term2",
    "XF86Launch5",
    groups=groups,
    keys=keys,
    dgroups=dgroups_app_rules,
    screen=TERTIARY_SCREEN,
)

Terminal(
    "salt-bison",
    [[mod], "F12"],
    groups=groups,
    keys=keys,
    dgroups=dgroups_app_rules,
    spawn=expanduser("~/.bin/salt-bison"),
    screen=SECONDARY_SCREEN,
)

Terminal(
    "comms",
    "F9",
    groups=groups,
    keys=keys,
    dgroups=dgroups_app_rules,
    screen=PRIMARY_SCREEN,
)

Terminal(
    "jupyter-bison",
    [[mod], "XF86Launch5"],
    groups=groups,
    keys=keys,
    dgroups=dgroups_app_rules,
    screen=SECONDARY_SCREEN,
    spawn="jupyter-bison",
)

Terminal(
    "jupyter-zebra",
    [[mod], "F11"],
    groups=groups,
    keys=keys,
    dgroups=dgroups_app_rules,
    screen=SECONDARY_SCREEN,
    spawn="jupyter-zebra",
)
Terminal(
    "htop",
    [
        ["control"],
        "Escape",
    ],
    groups=groups,
    keys=keys,
    dgroups=dgroups_app_rules,
    screen=TERTIARY_SCREEN,
    spawn=terminal("htop", cmd="htop"),
)

screens = get_screens(num_monitors, groups)


floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(wm_class="pinentry-qt"),  # GPG key password entry
        Match(
            title=[
                "discord.com is sharing your screen.",
            ],
        ),
        Match(wm_class=["Wine", "Xephyr", "Gmrun"]),
    ]
)
