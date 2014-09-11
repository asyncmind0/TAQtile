import logging
import re

from libqtile import layout
from libqtile.command import lazy
from libqtile.config import Key, Group, Match, Rule

from extra import SwitchGroup, MoveToGroup
from system import get_num_monitors
from themes import current_theme


log = logging.getLogger('qtile.config')

dgroups_key_binder = None

multi_monitor = get_num_monitors() > 1


def generate_groups(num_screens, keys, dgroups_app_rules, mod, layouts):
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
        Rule(Match(title=[re.compile(r"^Developer.*")]), group="12",
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
            re.compile(r".*wealth management support.*conkeror$", re.I),
        ]), group="11"),
        # Rule(Match(wm_class=["Conkeror"]), group="2"),
    ])

    num_groups = num_screens * 10
    log.debug("num_groups:%s", num_groups)
    groups = []
    for i in range(1, num_groups):
        layout_config = layout_map.get(i, layout_map[-1])
        groups.append(Group(
            str(i), layout=layout_config['name'],
            layouts=layout_config['layouts']))
    for i, g in enumerate(groups, 1):
        # mod1 + letter of group = switch to group
        # log.debug("group:%s", i)
        if i < 10:
            keys.append(
                Key([mod], str(i), lazy.function(SwitchGroup(i))))
            keys.append(
                Key([mod, "shift"], str(i),
                    lazy.function(MoveToGroup(i))))
    return groups
