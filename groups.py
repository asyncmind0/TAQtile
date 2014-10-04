import logging
import re

from libqtile import layout
from libqtile.command import lazy
from libqtile.config import Key, Group, Match, Rule

from system import get_num_monitors, get_hostconfig
from themes import current_theme

log = logging.getLogger('qtile.config')


def generate_groups(num_groups, num_monitors, dgroups_app_rules, layouts):
    multi_monitor = num_monitors > 1
    is_laptop = get_hostconfig('laptop')
    # layout map to restrict availiable layouts for a group
    layout_map = {
        3: {'name': "slice", 'layouts': [
            # a layout for pidgin
            layout.Slice('right', 256, role='buddy_list',
                         fallback=layout.Tile(**current_theme))]},
        6: {'name': "slice", 'layouts': [
            # a layout for hangouts
            layout.Slice('right', 356, wname="Hangouts",
                         fallback=layout.Tile(**current_theme))]},
        # fallback=layout.Stack(num_stacks=2, **border_args))]},
        -1: {'name': "max", 'layouts': layouts}
    }
    # dgroup rules that not belongs to any group
    dgroups_app_rules.extend([
        Rule(Match(title=[
            re.compile(r"^Developer.*"), re.compile(r"^Inspector.*")]),
             group="12" if multi_monitor and not is_laptop else "2",
             break_on_match=True),
        Rule(Match(title=[re.compile(r"^Hangouts.*")],
                   wm_instance_class=[re.compile(r"^crx_nck.*")]), group="6",
             break_on_match=True),
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
        Rule(Match(role=[re.compile("^kmail-mainwindow.*"),
                         re.compile("^kontact-mainwindow.*")]), group="mail",
             break_on_match=True),
        Rule(Match(wm_class=["Kmail", "Kontact"]), group="mail", float=False,
             break_on_match=True),
        Rule(Match(wm_class=["Pidgin"]), group="3", float=False),
        Rule(Match(wm_class=["KeePass2"]), float=True),
        Rule(Match(wm_class=["Kruler"]), float=True),
        Rule(Match(wm_class=["Screenkey"]), float=True, intrusive=True),
        Rule(Match(wm_class=["rdesktop"]), group="14"),
        Rule(Match(wm_class=[re.compile(r".*VirtualBox.*")]),
             group="13" if multi_monitor else "4"),
        Rule(Match(title=[
            re.compile(r".*iress development.*conkeror$", re.I),
            re.compile(r".*wealth management support.*conkeror$"),
        ]), group="11"),
        Rule(Match(title=["monitor"], wm_class=["InputOutput"]), group='monitor'),
        Rule(Match(title=["left"], wm_class=["InputOutput"]), group='left'),
        Rule(Match(title=["right"], wm_class=["InputOutput"]), group='right'),
        Rule(Match(title=["comm"], wm_class=["InputOutput"]), group='comm'),
        # Rule(Match(wm_class=["Conkeror"]), group="2"),
    ])

    log.debug("num_groups:%s", num_groups)
    groups = []
    # map og group and prefered screen
    screen_affinity = {
        'left': 1, 'right': 0, 'comm': 0, 'mail': 0, 'monitor': 0}
    for i in range(1, num_groups+1) + screen_affinity.keys():
        layout_config = layout_map.get(i, layout_map[-1])
        groups.append(Group(
            str(i), layout=layout_config['name'],
            layouts=layout_config['layouts'],
            screen_affinity=screen_affinity.get(str(i))))

    return groups
