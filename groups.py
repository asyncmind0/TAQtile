import logging
import re

from libqtile import layout
from libqtile.config import Group, Match, Rule

from system import get_hostconfig
from themes import current_theme
from collections import OrderedDict
from screens import PRIMARY_SCREEN, SECONDARY_SCREEN


log = logging.getLogger('qtile.config')


def generate_groups(num_groups, num_monitors, dgroups_app_rules, layouts):
    multi_monitor = num_monitors > 1
    is_laptop = get_hostconfig('laptop')

    # dgroup rules that not belongs to any group
    dgroups_app_rules.extend([
        # Everything i want to be float, but don't want to change group
        Rule(Match(title=['nested', 'gscreenshot'],
                   wm_class=['Guake.py', 'Exe', 'Onboard', 'Florence',
                             'Terminal', 'Gpaint', 'Kolourpaint', 'Wrapper',
                             'Gcr-prompter', 'Ghost',
                             re.compile('Gnome-keyring-prompt.*?')],
                   ),
             float=True, intrusive=True),

        # floating windows
        Rule(Match(wm_class=["Pavucontrol", 'Wine', 'Xephyr', "Gmrun"]),
             float=True),
        Rule(Match(wm_class=["Pidgin"]), group="3", float=False),
        Rule(Match(wm_class=["KeePass2"]), float=True),
        Rule(Match(wm_class=["Kruler"]), float=True),
        Rule(Match(wm_class=["Screenkey"]), float=True, intrusive=True),
        Rule(Match(title=[re.compile(".*Org Select.*")]),
             float=True, intrusive=True),
        Rule(Match(wm_class=["rdesktop"]), group="15"),
        Rule(Match(wm_class=[re.compile(r".*VirtualBox.*")]),
             group="13" if multi_monitor else "4"),
        Rule(Match(title=[
            re.compile(r".*iress development.*conkeror$", re.I),
            re.compile(r".*wealth management support.*conkeror$"),
        ]), group="11"),
        Rule(Match(title=[
            re.compile(r"^Developer.*"), re.compile(r"^Inspector.*")]),
             group="2", break_on_match=True),
        Rule(Match(role=[re.compile("^browser$")],
                   wm_class=["Google-chrome-stable"]),
             group="11" if multi_monitor else "1",
             break_on_match=False),
        Rule(Match(title=[re.compile(r"^Hangouts$")]), group="comm2",
             break_on_match=False),
        Rule(Match(role=[re.compile("^pop-up$")],
                   wm_instance_class=["^crx_.*"]),
             group="comm2", break_on_match=False),
    ])

    def terminal_matches(regexes):
        return [Match(
            title=[re.compile(regex) for regex in regexes],
            wm_class=["InputOutput"])]

    log.debug("num_groups:%s", num_groups)
    groups = []
    # map og group and prefered screen
    group_args = OrderedDict()
    group_args['comm1'] = dict(
        screen_affinity=SECONDARY_SCREEN,
        matches=terminal_matches([r"^comm$"]) + [Match(wm_class=["psi"])],
        layouts=[
            layout.Slice('right', 256, wname='Psi',
                         fallback=layout.Tile(**current_theme))
        ])
    group_args['comm2'] = dict(
        layout="slice",
        layouts=[
            #layout.Slice('right', 256, role='buddy_list',
            #             fallback=layout.Tile(**current_theme)),
            # a layout for hangouts
            layout.Slice(
                'right', 356, wname="Hangouts", role="pop-up",
                fallback=layout.Tile(**current_theme))])
    group_args['monitor'] = dict(
        screen_affinity=0, matches=terminal_matches([r"^monitor$"]))
    group_args['mail'] = dict(
        screen_affinity=get_hostconfig('screen_affinity').get('mail', 0),
        matches=[
            Match(wm_class=["Kmail", "Kontact"]),
            Match(role=[re.compile("^kmail-mainwindow.*"),
                        re.compile("^kontact-mainwindow.*")])]
        + terminal_matches([r"^mail$"]))
    group_args['term1'] = dict(
        screen_affinity=1, exclusive=False,
        matches=terminal_matches([r"^iress_right$", "^left$"]))
    group_args['term2'] = dict(
        screen_affinity=0, exclusive=False,
        matches=terminal_matches(["^iress_left$", "^right$"]))
    if not is_laptop:
        group_args['remote_term1'] = dict(
            screen_affinity=1, exclusive=False,
            matches=terminal_matches([r"^remote_term1$"]))
        group_args['remote_term2'] = dict(
            screen_affinity=0, exclusive=False,
            matches=terminal_matches(["^remote_term2$"]))
        group_args['htop'] = dict(
            screen_affinity=SECONDARY_SCREEN,
            persist=False,
            matches=terminal_matches([r"^htop$"]))
        group_args['log'] = dict(
            screen_affinity=SECONDARY_SCREEN,
            persist=False,
            matches=terminal_matches([r"^log$"]))
        group_args['ulog'] = dict(
            screen_affinity=SECONDARY_SCREEN,
            persist=False,
            matches=terminal_matches([r"^ulog$"]))

    for i in range(1, num_groups+1) + group_args.keys():
        groups.append(Group(
            str(i), **group_args.get(
                str(i), {'layout': "max", 'layouts': layouts})))

    return groups
