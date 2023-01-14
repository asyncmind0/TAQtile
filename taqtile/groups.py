import re
import struct
from collections import OrderedDict

from libqtile.config import Group, Match, Rule as QRule, ScratchPad, DropDown

from taqtile.log import logger
from taqtile.screens import SECONDARY_SCREEN, PRIMARY_SCREEN
from taqtile.system import get_hostconfig, get_group_affinity


class Rule(QRule):
    def __init__(
        self,
        match,
        front=False,
        fullscreen=False,
        static=False,
        opacity=None,
        center=False,
        current_screen=False,
        geometry=None,
        **kwargs
    ):
        super().__init__(match, **kwargs)
        self.front = front
        self.fullscreen = fullscreen
        self.static = static
        self.opacity = opacity
        self.center = center
        self.current_screen = current_screen
        self.geometry = geometry


def is_mailbox(client):
    try:
        surf_uri = client.window.get_property("_SURF_URI", str)
    except struct.error:
        return False

    if surf_uri and surf_uri.startswith("https://mail.google.com"):
        return True
    return False


def get_dgroups():
    return [
        Rule(
            Match(
                title=[
                    re.compile("^Android Emulator.*"),
                    re.compile("^Emulator.*"),
                ]
            ),
            float=True,
            intrusive=True,
            group=get_group_affinity("emulator"),
        ),
        Rule(
            Match(func=is_mailbox),
            group="mail",
            break_on_match=True,
        ),
        Rule(
            Match(
                title=[
                    re.compile(r"^Developer.*", re.I),
                    re.compile(r"^Devtools.*", re.I),
                    re.compile(r"^Inspector.*", re.I),
                    re.compile(r"^chrome-devtools.*", re.I),
                ]
            ),
            group=get_group_affinity("devtools"),
            break_on_match=True,
        ),
        Rule(
            Match(
                title=[
                    re.compile(r"^Hangouts$"),
                    re.compile(r"^yakyak$", re.I),
                    re.compile(r"^Signal$", re.I),
                ]
            ),
            group=get_group_affinity("hangouts"),
            break_on_match=False,
        ),
        Rule(
            Match(
                wm_class=[re.compile("^crx_.*")],
                wm_instance_class=[re.compile("^crx_.*")],
            ),
            group=get_group_affinity("hangouts"),
            break_on_match=False,
        ),
        Rule(
            Match(
                title=[re.compile(r"whatsapp.*", re.I)],
                wm_class=[re.compile(".*whatsapp.*", re.I)],
            ),
            group=get_group_affinity("whatsapp"),
            break_on_match=False,
        ),
        Rule(
            Match(title=[re.compile(r"klipper", re.I)]),
            group="3",
            break_on_match=False,
        ),
        Rule(
            Match(title=[re.compile(r".*discord.*", re.I)]),
            group="webcon",
            break_on_match=False,
        ),
        Rule(
            Match(
                wm_class=[re.compile("insync.*", re.I)],
                wm_instance_class=[re.compile("insync.*", re.I)],
            ),
            # float=True,
            static=True,
            break_on_match=True,
        ),
    ]


def generate_groups(num_groups, layouts):
    is_laptop = get_hostconfig("laptop")

    # dgroup rules that not belongs to any group

    def terminal_matches(regexes):
        return [
            Match(
                title=[re.compile(regex) for regex in regexes],
                # wm_class=["InputOutput", "xterm-256color"]
            )
        ]

    logger.debug("num_groups:%s", num_groups)
    groups = []
    # map og group and prefered screen
    group_args = OrderedDict(
        {
            "monitor": dict(
                screen_affinity=PRIMARY_SCREEN,
                matches=terminal_matches([r"^monitor$"])
                + [Match(title=[re.compile(r"System Monitor", re.I)])],
            ),
            "mail": dict(
                screen_affinity=PRIMARY_SCREEN,
                exclusive=True,
                init=True,
                matches=[
                    Match(func=is_mailbox),
                    Match(
                        title=[re.compile(".*mail.*", re.I)],
                        wm_class=["brave-browser"],
                    ),
                ]
                + terminal_matches([r"^mail$"]),
            ),
            "cal": dict(
                screen_affinity=PRIMARY_SCREEN,
                exclusive=False,
                init=True,
                matches=[
                    Match(
                        wm_instance_class=[re.compile("calendar.google.com.*")]
                    )
                ],
            ),
            "browser": dict(
                screen_affinity=SECONDARY_SCREEN,
                init=True,
                persist=True,
                matches=[
                    Match(wm_class=["brave-browser"]),
                    Match(wm_class=["qutebrowser"]),
                    Match(wm_instance_class=["surf"]),
                    Match(role=["browser"]),
                ],
            ),
            "social": dict(
                screen_affinity=PRIMARY_SCREEN,
                init=True,
                persist=True,
                matches=[
                    Match(title=[re.compile(r".*twitter\.com.*", re.I)]),
                    Match(title=[re.compile(r".*diamondapp\.com.*", re.I)]),
                ],
            ),
            "slack": dict(
                screen_affinity=PRIMARY_SCREEN,
                init=True,
                persist=True,
                matches=[
                    Match(wm_class=["zoom"]),
                    Match(wm_class=["slack"]),
                    # Match(role=[re.compile("^slack$")], wm_class=["slack"]),
                ],
            ),
            "webcon": dict(
                screen_affinity=PRIMARY_SCREEN,
                init=True,
                persist=True,
                matches=[
                    Match(wm_class=["discord"]),
                    Match(title=[re.compile(r".*discord.*", re.I)]),
                    Match(title=[re.compile(r".*whatsapp.*", re.I)]),
                    Match(wm_class=["telegram-desktop"]),
                    # Match(role=[re.compile("^slack$")], wm_class=["slack"]),
                ],
            ),
            "krusader": dict(
                screen_affinity=PRIMARY_SCREEN,
                persist=False,
                matches=[Match(title=[".*krusader.*"], wm_class=["Krusader"])],
            ),
            "emacs": dict(
                screen_affinity=PRIMARY_SCREEN,
                persist=True,
                matches=[
                    Match(wm_class=["emacs"]),
                    Match(wm_class=["jetbrains-studio"]),
                ],
            ),
        }
    )
    if not is_laptop:
        group_args["htop"] = dict(
            screen_affinity=SECONDARY_SCREEN,
            persist=False,
            matches=terminal_matches([r"^htop$"]),
        )
        group_args["log"] = dict(
            screen_affinity=SECONDARY_SCREEN,
            persist=False,
            matches=terminal_matches([r"^log$"]),
        )
        group_args["ulog"] = dict(
            screen_affinity=SECONDARY_SCREEN,
            persist=False,
            matches=terminal_matches([r"^ulog$"]),
        )

    for i in range(1, num_groups + 1):
        groups.append(
            Group(
                str(i),
                label=str(i)[-1] if i > 9 else str(i),
                **group_args.get(str(i), {"layout": "max", "layouts": layouts})
            )
        )
    for i, groupargs in group_args.items():
        groups.append(Group(str(i), **groupargs))
    groups.append(
        ScratchPad(
            "scratch",
            dropdowns=[
                DropDown(
                    name="xterm",
                    cmd="xterm",
                ),
                DropDown(
                    name="htop",
                    cmd="st -t htop -e htop",
                ),
                DropDown(
                    name="ncpamixer",
                    cmd="st -t pamixer -e ncpamixer",
                    height=1,
                ),
            ],
        )
    )
    return groups
