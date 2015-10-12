import logging

import system
import themes
from libqtile import bar, widget
from libqtile.config import Screen
from widgets import CalClock
from widgets.bankbalance import BankBalance
from widgets.multiscreengroupbox import MultiScreenGroupBox
from widgets.priority_notify import PriorityNotify
from widgets.tasklist2 import TaskList2


log = logging.getLogger('qtile')

PRIMARY_SCREEN = system.get_screen(0)
SECONDARY_SCREEN = system.get_screen(1)
PRIMARY_MONITOR = 0
SECONDARY_MONITOR = 1



def get_screens(num_monitors, num_groups, groups):
    screens = []
    multi_monitor = num_monitors > 1

    def default_params(**kwargs):
        de = dict(themes.current_theme)
        de.update(kwargs)
        return de

    groupbox_params = default_params(
        urgent_alert_method='text',
        rounded=False,
        padding=-1,
        border_width=1,
        borderwidth=1,
        border_focus='#FFFFFF',
        linewidth=1,
    )

    prompt_params = default_params()
    systray_params = default_params()
    current_layout_params = default_params(
        name="default", padding=2)
    #windowname_params = default_params
    systray_params = default_params()
    clock_params = default_params(padding=2, format='%Y-%m-%d %a %H:%M')
    pacman_params = default_params()
    notify_params = default_params()
    bitcointicker_params = default_params()
    batteryicon_params = default_params()
    batteryicon_params['battery_name'] = "BAT1"
    batteryicon_params['format'] = "{percent:5.0%}"
    windowtabs_params = default_params(selected=("[", "]"), separator='|')
    tasklist_params = default_params(
        fontsize=12,
        selected=("[", "]"),
        separator='|',
        rounded=False,
        padding_x=2,
        padding_y=0,
        margin_y=0,
        margin_x=0,
        border=themes.current_theme['border_focus'],
        #foreground=themes.current_theme['foreground'],
    )

    graph_defaults = {k[0]: k[1] for k in[
        ("graph_color", "18BAEB.6", "Graph color"),
        ("fill_color", "1667EB.3", "Fill color for linefill graph"),
        ("border_color", "215578", "Widget border color"),
        ("border_width", 1, "Widget border width"),
        ("margin_x", 1, "Margin X"),
        ("margin_y", 1, "Margin Y"),
        ("samples", 100, "Count of graph samples."),
        ("frequency", 1, "Update frequency in seconds"),
        ("type", "linefill", "'box', 'line', 'linefill'"),
        ("line_width", 1, "Line width"),
        ("start_pos", "bottom", "Drawer starting position ('bottom'/'top')"),
        ("width", 50, "Width")
    ]}
    cpugraph_params = dict(graph_defaults)
    cpugraph_params["graph_color"] = "FF3333.6"
    cpugraph_params["fill_color"] = "FF3333.3"
    memgraph_params = dict(graph_defaults)
    memgraph_params['graph_color'] = "80FF00.6"
    memgraph_params['fill_color'] = "80FF00.3"
    memgraph_params['type'] = "linefill"
    netgraph_params = dict(graph_defaults)
    sep_params = default_params(padding=2, fontsize=9, height_percent=60)
    # netgraph_params['fill_color'] = "80FF00.3"

    group_splits = ((num_groups / num_monitors) if multi_monitor else num_groups,)
    # change labels of groups for multi monitor support
    mon_map = {0: {}, 1: {}}
    mon = 0
    for i, group in enumerate(groups):
        if group.name.isdigit():
            if multi_monitor and int(group.name)-1 in group_splits:
                mon += 1
        groupname = group.name
        grouplabel = group.name[-1] if group.name.isdigit() else group.name
        if group.screen_affinity is None or not multi_monitor:
            mon_map[mon][groupname] = grouplabel
        else:
            mon_map[group.screen_affinity][groupname] = grouplabel

    primary_bar = [
        #widget.GroupBox(**groupbox_params),
        MultiScreenGroupBox(
            namemap=mon_map[PRIMARY_SCREEN], **groupbox_params),
        widget.Sep(**sep_params),
        widget.Prompt(**prompt_params),
        widget.Sep(**sep_params),
        TaskList2(**tasklist_params),
        # widget.WindowName(**windowname_params),
        # widget.TextBox(**layout_textbox_params),
        widget.Sep(**sep_params),
        widget.CurrentLayout(**current_layout_params),
        widget.Sep(**sep_params),
        # widget.BitcoinTicker(**bitcointicker_params),
        # widget.Sep(**sep_params),
        #ThreadedPacman(**pacman_params),
        widget.Sep(**sep_params),
        widget.DF(**default_params()),
        widget.Sep(**sep_params),
        BankBalance(**default_params()),
        widget.Sep(**sep_params),
        PriorityNotify(**default_params()),
        # widget.Image(filename="/usr/share/icons/oxygen/16x16/devices/cpu.png"),
        widget.Sep(**sep_params),
        widget.TextBox("c:", **default_params()),
        widget.CPUGraph(**cpugraph_params),
        # widget.Image(filename="/usr/share/icons/oxygen/16x16/devices/media-flash-memory-stick.png"),
        widget.TextBox("m:", **default_params()),
        widget.MemoryGraph(**memgraph_params),
        # widget.Image(filename="/usr/share/icons/oxygen/16x16/devices/network-wired.png"),
        widget.TextBox("n:", **default_params()),
        widget.NetGraph(**netgraph_params),
        # widget.Sep(**sep_params),
        # widget.Notify(width=30, **notify_params),
        widget.Sep(**sep_params)
    ]
    if system.get_hostconfig('battery'):
        primary_bar.append(widget.Battery(**batteryicon_params))
        primary_bar.append(widget.Sep(**sep_params))
    primary_bar.append(widget.Systray(**systray_params))
    primary_bar.append(CalClock(**clock_params))

    secondary_bar = [
        #widget.GroupBox(**groupbox_params),
        MultiScreenGroupBox(
            namemap=mon_map[SECONDARY_SCREEN], **groupbox_params),
        widget.Sep(**sep_params),
        TaskList2(**tasklist_params),
        widget.Sep(**sep_params),
        widget.CurrentLayout(**current_layout_params),
        widget.Sep(**sep_params),
        CalClock(**clock_params),
    ]
    bar_map = {0: primary_bar, 1: secondary_bar}
    bar_height = groupbox_params.get('bar_height', 10)
    screens.append(Screen(bar.Bar(bar_map[PRIMARY_SCREEN], bar_height)))
    if num_monitors > 1:
        screens.append(Screen(bar.Bar(bar_map[SECONDARY_SCREEN], bar_height)))
    return screens
