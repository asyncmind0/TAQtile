import logging
import re

from libqtile import layout
from libqtile.config import Group, Match, Rule

from system import get_hostconfig, get_group_affinity, get_screen_affinity
from themes import current_theme
from collections import OrderedDict
from screens import SECONDARY_SCREEN, PRIMARY_SCREEN


log = logging.getLogger('qtile.config')


def generate_groups(num_groups, num_monitors, dgroups_app_rules, layouts):
    is_laptop = get_hostconfig('laptop')

    # dgroup rules that not belongs to any group
    dgroups_app_rules.extend([
        # Everything i want to be float, but don't want to change group
        Rule(
            Match(
                title=['nested', 'gscreenshot'],
                wm_class=[
                    'Guake.py', 'Exe', 'Onboard', 'Florence',
                    'Terminal', 'Gpaint', 'Kolourpaint', 'Wrapper',
                    'Gcr-prompter', 'Ghost',
                    re.compile('Gnome-keyring-prompt.*?')
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
            float=True),
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
                title=['pinentry']
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
            group="11"
        ),
        Rule(
            Match(
                title=[
                    re.compile(r"^Developer.*"),
                    re.compile(r"^Devtools.*"),
                    re.compile(r"^Inspector.*")
                ],
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
                title=[re.compile(r"^Hangouts$")]
            ),
            group="comm2",
            break_on_match=False
        ),
        Rule(
            Match(
                wm_class=[re.compile("^crx_.*")],
                wm_instance_class=[re.compile("^crx_.*")]
            ),
            group="comm2",
            break_on_match=False
        ),
    ])

    def terminal_matches(regexes):
        return [
            Match(
                title=[re.compile(regex) for regex in regexes],
                #wm_class=["InputOutput", "xterm-256color"]
            )
        ]

    log.debug("num_groups:%s", num_groups)
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
        'comm2': dict(
            screen_affinity=SECONDARY_SCREEN,
            #layout="slice",
            #layouts=[
            #    # layout.Slice('right', 256, role='buddy_list',
            #    #             fallback=layout.Tile(**current_theme)),
            #    # a layout for hangouts
            #    layout.Slice(
            #        'right', 356, wname="Hangouts", role="pop-up",
            #        fallback=layout.Tile(**current_theme))
            #]
        ),
        'monitor': dict(
            screen_affinity=PRIMARY_SCREEN,
            matches=terminal_matches([r"^monitor$"])
        ),
        'mail': dict(
            screen_affinity=get_screen_affinity('mail'),
            init=True,
            matches=[
                Match(wm_class=["Kmail", "Kontact"]),
                Match(
                    role=[
                        re.compile("^kmail-mainwindow.*"),
                        re.compile("^kontact-mainwindow.*")
                    ]
                )
            ] + terminal_matches([r"^mail$"])
        ),
        'term1': dict(
            screen_affinity=PRIMARY_SCREEN,
            exclusive=False,
            init=True,
            matches=terminal_matches([r".*_right$", r"^left$"])
        ),
        'term2': dict(
            screen_affinity=SECONDARY_SCREEN,
            exclusive=False,
            init=True,
            matches=terminal_matches([r".*_left$", r"^right$"])
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
