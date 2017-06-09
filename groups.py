import logging
import re

from libqtile import layout
from libqtile.config import Group, Match, Rule as QRule

from system import get_hostconfig, get_group_affinity, get_screen_affinity
from themes import current_theme
from collections import OrderedDict
from screens import SECONDARY_SCREEN, PRIMARY_SCREEN

from log import logger


class Rule(QRule):
    def __init__(
            self, match, front=False, fullscreen=False,
            static=False, opacity=None, center=False,
            current_screen=False,
            **kwargs
            ):
        super(Rule, self).__init__(match, **kwargs)
        self.front = front
        self.fullscreen = fullscreen
        self.static = static
        self.opacity = opacity
        self.center = center
        self.current_screen = current_screen


def generate_groups(num_groups, num_monitors, dgroups_app_rules, layouts):
    is_laptop = get_hostconfig('laptop')

    # dgroup rules that not belongs to any group
    dgroups_app_rules.extend([
        Rule(
            Match(
                wm_class=[re.compile(".*dunst.*", re.I)],
            ),
            group="1",
            break_on_match=True,
            static=True,
        ),
        Rule(
            Match(
                title=["pinentry-qt"],
            ),
            break_on_match=True,
            float=True,
            intrusive=True,
            front=True,
            center=True,
        ),
        # Everything i want to be float, but don't want to change group
        Rule(
            Match(
                title=['nested', 'gscreenshot'],
                wm_class=[
                    'Guake.py', 'Exe', 'Onboard', 'Florence',
                    'Terminal', 'Gpaint', 'Kolourpaint', 'Wrapper',
                    'Gcr-prompter', 'Ghost',
                    re.compile('Gnome-keyring-prompt.*?'),
                    "SshAskpass",
                    "ssh-askpass",
                    "zoom",
                ],
            ),
            float=True,
            intrusive=True
        ),
        Rule(
            Match(
                wm_class=["Pavucontrol", 'Wine', 'Xephyr', "Gmrun"]
            ),
            float=True
        ),
        Rule(
            Match(
                wm_class=["Pidgin"]
            ),
            group="3",
            float=False
        ),
        Rule(
            Match(
                wm_class=[
                    "KeePass2",
                    "Kruler",
                    "Torbrowser-launcher",
                ]
            ),
            float=True
        ),
        Rule(
            Match(
                title=[
                    re.compile("^Android Emulator.*"),
                    re.compile("^Emulator.*"),
                ]
            ),
            float=True,
            intrusive=True,
            group=get_group_affinity('emulator'),
        ),
        Rule(
            Match(
                wm_class=["Screenkey"]
            ),
            float=True,
            intrusive=True
        ),
        Rule(
            Match(
                title=[re.compile(".*Org Select.*")]
            ),
            float=True,
            intrusive=True
        ),
        Rule(
            Match(
                wm_class=["rdesktop"]
            ),
            group=get_group_affinity('rdesktop'),
        ),
        Rule(
            Match(
                wm_class=[
                    re.compile(r".*VirtualBox.*")
                ]
            ),
            group=get_group_affinity('virtualbox'),
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
        Rule(
            Match(
                title=[
                    re.compile(r"^Developer.*", re.I),
                    re.compile(r"^Devtools.*", re.I),
                    re.compile(r"^Inspector.*", re.I),
                    re.compile(r"^chrome-devtools.*", re.I)
                ],
            ),
            group=get_group_affinity("devtools"),
            break_on_match=True,
        ),
        Rule(
            Match(
                wm_class=["Transgui"],
            ),
            group=get_group_affinity('transgui'),
        ),
        Rule(
            Match(
                role=[re.compile("^browser$")],
                wm_class=["Google-chrome-stable"]),
            group=get_group_affinity('browser'),
            break_on_match=False
        ),
        Rule(
            Match(
                title=[
                    re.compile(r"^Hangouts$"),
                    re.compile(r".*whatsi.*", re.I),
                ]
            ),
            group=get_group_affinity("hangouts"),
            break_on_match=False,
        ),
        Rule(
            Match(
                wm_class=[re.compile("^crx_.*")],
                wm_instance_class=[re.compile("^crx_.*")]
            ),
            group=get_group_affinity("hangouts"),
            break_on_match=False
        ),
        Rule(
            Match(
                title=[re.compile(r"slack.*", re.I)]
                #wm_class=[re.compile(".*slack.*", re.I)],
                #wm_instance_class=[re.compile(".*slack.*", re.I)]
            ),
            group=get_group_affinity("slack"),
            break_on_match=False,
        ),

        Rule(
            Match(
                wm_class=[re.compile(".*insync\.py.*", re.I)],
                wm_instance_class=[re.compile(".*insync\.py.*", re.I)]
            ),
            float=True,
            break_on_match=False
        ),
        Rule(
            Match(
                title="shrapnel",
            ),
            group="1",
            break_on_match=False,
            float=True,
            opacity=0.85,
        ),
    ])

    def terminal_matches(regexes):
        return [
            Match(
                title=[re.compile(regex) for regex in regexes],
                #wm_class=["InputOutput", "xterm-256color"]
            )
        ]

    logger.debug("num_groups:%s", num_groups)
    groups = []
    # map og group and prefered screen
    group_args = OrderedDict({
        'comm1': dict(
            screen_affinity=PRIMARY_SCREEN,
            matches=terminal_matches([r"^comm1$"])
            # matches=terminal_matches([r"^comm$"]) + [
            #    Match(wm_class=[re.compile(r'psi.*', re.I)])],
            # layouts=[
            #    layout.Slice(
            #        'right', 256,
            #        wname="Psi+",
            # wmclass="Psi-plus",
            #        fallback=layout.Tile(**current_theme))
            #]
        ),
        'monitor': dict(
            screen_affinity=PRIMARY_SCREEN,
            matches=terminal_matches([r"^monitor$"])
        ),
        'mail': dict(
            screen_affinity=PRIMARY_SCREEN, #get_screen_affinity('mail'),
            exclusive=False,
            init=True,
            matches=[
                Match(wm_class=["Kmail", "Kontact"]),
                Match(
                    title=[
                        re.compile("^Inbox .*"),
                    ]
                ),
                Match(
                    role=[
                        re.compile("^kmail-mainwindow.*"),
                        re.compile("^kontact-mainwindow.*"),
                    ]
                )
            ] + terminal_matches([r"^mail$"])
        ),
        'cal': dict(
            screen_affinity=PRIMARY_SCREEN, #get_screen_affinity('mail'),
            exclusive=False,
            init=True,
            matches=[
                Match(
                    wm_instance_class=[re.compile("calendar.google.com.*")]
                )
            ]
        ),
        'term1': dict(
            screen_affinity=PRIMARY_SCREEN,
            exclusive=False,
            init=True,
            matches=terminal_matches([r"left", r"^shawk_left$"])
        ),
        'term2': dict(
            screen_affinity=SECONDARY_SCREEN,
            exclusive=False,
            init=True,
            matches=terminal_matches([r"right", r"^shawk_right$"])
        ),
        'azure_left': dict(
            screen_affinity=PRIMARY_SCREEN,
            exclusive=False,
            init=True,
            matches=terminal_matches([r"^azure_left$", r"staging"])
        ),
        'azure_right': dict(
            screen_affinity=SECONDARY_SCREEN,
            exclusive=False,
            init=True,
            matches=terminal_matches([r"^azure_right$"])
        ),
        'krusader': dict(
            screen_affinity=SECONDARY_SCREEN,
            persist=False,
            matches=[
                Match(
                    title=[".*krusader.*"],
                    wm_class=["Krusader"],
                ),
            ]
        )
    })
    if not is_laptop:
        group_args['remote_term1'] = dict(
            screen_affinity=PRIMARY_SCREEN,
            exclusive=False,
            matches=terminal_matches(
                [r"^remote_term1$"])
        )
        group_args['remote_term2'] = dict(
            screen_affinity=SECONDARY_SCREEN,
            exclusive=False,
            matches=terminal_matches(["^remote_term2$"])
        )
        group_args['htop'] = dict(
            screen_affinity=SECONDARY_SCREEN,
            persist=False,
            matches=terminal_matches([r"^htop$"])
        )
        group_args['log'] = dict(
            screen_affinity=SECONDARY_SCREEN,
            persist=False,
            matches=terminal_matches([r"^log$"])
        )
        group_args['ulog'] = dict(
            screen_affinity=SECONDARY_SCREEN,
            persist=False,
            matches=terminal_matches([r"^ulog$"])
        )

    from itertools import chain
    for i in chain(range(1, num_groups + 1), group_args.keys()):
        groups.append(
            Group(
                str(i), **group_args.get(
                    str(i), {'layout': "max", 'layouts': layouts}
                )
            )
        )

    return groups
