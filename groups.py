import logging
import re

from libqtile import layout
from libqtile.config import Group, Match, Rule as QRule, ScratchPad, DropDown

from system import get_hostconfig, get_group_affinity, get_screen_affinity
from themes import current_theme
from collections import OrderedDict
from screens import SECONDARY_SCREEN, PRIMARY_SCREEN
from itertools import chain
from extra import terminal

from log import logger


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
        super(Rule, self).__init__(match, **kwargs)
        self.front = front
        self.fullscreen = fullscreen
        self.static = static
        self.opacity = opacity
        self.center = center
        self.current_screen = current_screen
        self.geometry = geometry


def generate_groups(num_groups, num_monitors, dgroups_app_rules, layouts):
    is_laptop = get_hostconfig("laptop")

    # dgroup rules that not belongs to any group
    dgroups_app_rules.extend(
        [
            Rule(Match(title=["TDE World Clock"]), break_on_match=True, float=True),
            Rule(
                Match(wm_class=[re.compile(".*dunst.*", re.I)]),
                group="1",
                break_on_match=True,
                static=True,
            ),
            Rule(
                Match(title=["pinentry-qt"], wm_class=["Ksnapshot"]),
                break_on_match=True,
                float=True,
                intrusive=True,
                front=True,
                center=True,
            ),
            # Everything i want to be float, but don't want to change group
            Rule(
                Match(
                    title=["nested", "gscreenshot"],
                    wm_class=[
                        "Guake.py",
                        "Exe",
                        "Onboard",
                        "Florence",
                        "Terminal",
                        "Gpaint",
                        "Kolourpaint",
                        "Wrapper",
                        "Gcr-prompter",
                        "Ghost",
                        re.compile("Gnome-keyring-prompt.*?"),
                        "SshAskpass",
                        "ssh-askpass",
                        "zoom",
                    ],
                ),
                float=True,
                intrusive=True,
            ),
            Rule(
                Match(wm_class=["Pavucontrol", "Wine", "Xephyr", "Gmrun"]), float=True
            ),
            Rule(Match(wm_class=["Pidgin"]), group="3", float=False),
            Rule(
                Match(wm_class=["KeePass2", "Kruler", "Torbrowser-launcher"]),
                float=True,
            ),
            Rule(
                Match(
                    wm_class=["jetbrains-studio", ]
                ),
                group=get_group_affinity('android-studio'),
                fullscreen=False,
                #break_on_match=True,
            ),
            Rule(
                Match(
                    wm_class=["Screenkey"]
                )
            ),
            Rule(
                Match(
                    title=[re.compile("^Android Emulator.*"), re.compile("^Emulator.*")]
                ),
                float=True,
                intrusive=True,
                group=get_group_affinity("emulator"),
            ),
            Rule(
                Match(
                    wm_class=["jetbrains-studio", ]
                ),
                group=get_group_affinity('android-studio'),
                fullscreen=False,
                #break_on_match=True,
            ),
            Rule(Match(wm_class=["Screenkey"]), float=True, intrusive=True),
            Rule(
                Match(title=[re.compile(".*Org Select.*")]), float=True, intrusive=True
            ),
            Rule(Match(wm_class=["rdesktop"]), group=get_group_affinity("rdesktop")),
            Rule(
                Match(wm_class=[re.compile(r".*VirtualBox.*")]),
                group=get_group_affinity("virtualbox"),
            ),
            Rule(
                Match(
                    title=[
                        re.compile(r".*iress development.*conkeror$", re.I),
                        re.compile(r".*wealth management support.*conkeror$"),
                    ]
                ),
                group="11",
                fullscreen=False,
                float=False,
            ),
            Rule(Match(wm_class=["Transgui"]), group=get_group_affinity("transgui")),
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
            #Rule(
            #    Match(role=[re.compile("^browser$")], wm_class=["webmacs"]),
            #    group=get_group_affinity("browser"),
            #    break_on_match=False,
            #),
            Rule(
                Match(title=[re.compile(r"^Hangouts$"), re.compile(r"^yakyak$", re.I)]),
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
                    wm_class=[re.compile(".*slack.*", re.I)],
                ),
                group=get_group_affinity("slack"),
                break_on_match=False,
            ),
            Rule(
                Match(
                    title=[re.compile(r"whatsapp.*", re.I)],
                    wm_class=[re.compile("^whats-app.*", re.I)],
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
                Match(
                    title=[re.compile(r".*discord.*", re.I)]
                    # wm_class=[re.compile(".*slack.*", re.I)],
                    # wm_instance_class=[re.compile(".*slack.*", re.I)]
                ),
                group=get_group_affinity("discord"),
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
            Rule(
                Match(title="shrapnel"),
                group="1",
                break_on_match=False,
                float=True,
                opacity=0.85,
            ),
        ]
    )

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
            "comm": dict(
                screen_affinity=PRIMARY_SCREEN,
                matches=terminal_matches([r"^comm$"])
                + [Match(title=[re.compile(r"System Monitor", re.I)])],
                # matches=terminal_matches([r"^comm$"]) + [
                #    Match(wm_class=[re.compile(r'psi.*', re.I)])],
                # layouts=[
                #    layout.Slice(
                #        'right', 256,
                #        wname="Psi+",
                # wmclass="Psi-plus",
                #        fallback=layout.Tile(**current_theme))
                # ]
            ),
            "monitor": dict(
                screen_affinity=PRIMARY_SCREEN, matches=terminal_matches([r"^monitor$"])
            ),
            "mail": dict(
                screen_affinity=PRIMARY_SCREEN,
                exclusive=False,
                init=True,
                matches=[
                    Match(wm_class=["Kmail", "Kontact"]),
                    Match(wm_class=[re.compile("mail.google.com__mail_u_.*")]),
                    Match(title=[re.compile("^Inbox .*")]),
                    Match(
                        role=[
                            re.compile("^kmail-mainwindow.*"),
                            re.compile("^kontact-mainwindow.*"),
                        ]
                    ),
                ]
                + terminal_matches([r"^mail$"]),
            ),
            "cal": dict(
                screen_affinity=PRIMARY_SCREEN,  # get_screen_affinity('mail'),
                exclusive=False,
                init=True,
                matches=[
                    Match(wm_instance_class=[re.compile("calendar.google.com.*")])
                ],
            ),
            "browser": dict(
                screen_affinity=PRIMARY_SCREEN,  # get_screen_affinity('mail'),
                persist=False,
                matches=[
                    Match(wm_instance_class=["surf"]),
                    Match(role=[re.compile("^browser$")], wm_class=["webmacs"]),
                ],
            ),
            "term1": dict(
                screen_affinity=PRIMARY_SCREEN,
                exclusive=False,
                init=True,
                matches=terminal_matches([r"left", r"^shawk_left$"]),
            ),
            "term2": dict(
                screen_affinity=SECONDARY_SCREEN,
                exclusive=False,
                init=True,
                matches=terminal_matches([r"right", r"^shawk_right$"]),
            ),
            "azure_left": dict(
                screen_affinity=PRIMARY_SCREEN,
                exclusive=False,
                init=True,
                matches=terminal_matches([r"^bison_left$", r"zebra_left"]),
            ),
            "azure_right": dict(
                screen_affinity=SECONDARY_SCREEN,
                exclusive=False,
                init=True,
                matches=terminal_matches([r"^bison_right$", r"zebra_right"]),
            ),
            "krusader": dict(
                screen_affinity=SECONDARY_SCREEN,
                persist=False,
                matches=[Match(title=[".*krusader.*"], wm_class=["Krusader"])],
            ),
        }
    )
    if not is_laptop:
        group_args["remote_term1"] = dict(
            screen_affinity=PRIMARY_SCREEN,
            exclusive=False,
            matches=terminal_matches([r"^remote_term1$"]),
        )
        group_args["remote_term2"] = dict(
            screen_affinity=SECONDARY_SCREEN,
            exclusive=False,
            matches=terminal_matches(["^remote_term2$"]),
        )
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

    for i in chain(range(1, num_groups + 1), group_args.keys()):
        groups.append(
            Group(
                str(i), **group_args.get(str(i), {"layout": "max", "layouts": layouts})
            )
        )
    groups.append(
        ScratchPad(
            'scratch',
            dropdowns=[
                DropDown(
                    name='xterm',
                    cmd='xterm',
                ),
                DropDown(
                    name='htop',
                    cmd='st -t htop -e htop',
                ),
                DropDown(
                    name='pavucontrol',
                    cmd='pavucontrol',
                    height=1,
                ),
            ]
        )
    )
    return groups
