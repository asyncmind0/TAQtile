import logging

import system
import themes
from libqtile.config import Screen
from widgets import (
    CalClock,
    Clock,
)
from libqtile.widget import (
    Sep,
    Pomodoro,
    WindowName,
    CurrentLayout,
    Battery,
    NetGraph,
    MemoryGraph,
    CPUGraph,
    Systray,
    DF,
    TextBox,
)

# from widgets.bankbalance import BankBalance
# from widgets.mail import NotmuchCount
from widgets.multiscreengroupbox import MultiScreenGroupBox

# from widgets.priority_notify import PriorityNotify
# from widgets.tasklist2 import TaskList2
from widgets.bar import Bar
from log import logger
from subprocess import check_output


log = logging.getLogger("qtile")

PRIMARY_SCREEN = system.get_screen(0)
SECONDARY_SCREEN = system.get_screen(1)
TERTIARY_SCREEN = system.get_screen(2)
QUATERNARY_SCREEN = system.get_screen(3)

try:
    localtimezone = check_output(["tzupdate", "-p", "-s", "5"]).decode().strip()
except:
    log.exception("Failed to automatically set timezone")
    localtimezone = "Australia/Sydney"


def get_screens(num_monitors, num_groups, groups):
    multi_monitor = num_monitors > 1

    def default_params(**kwargs):
        de = dict(themes.current_theme)
        de.update(kwargs)
        return de

    groupbox_params = default_params(
        urgent_alert_method="text",
        rounded=False,
        border_focus="#FFFFFF",
        is_line=False,
        center_aligned=True,
        hide_unused=True,
        spacing=2,
    )
    tasklist_params = default_params(
        selected=("[", "]"),
        rounded=False,
        border=themes.current_theme["border_focus"],
        icon_size=0,
        padding=0,
        padding_y=0,
        margin=0,
        foreground=themes.current_theme["foreground"],
    )

    # prompt_params = default_params()
    current_layout_params = default_params(name="default")
    windowname_params = default_params()
    systray_params = default_params(icon_size=15)
    clock_params = default_params(
        padding=2,
        format="%Y-%m-%d %a %H:%M",
    )
    pacman_params = default_params()
    notify_params = default_params()
    bitcointicker_params = default_params()
    batteryicon_params = default_params(
        charge_char="^",
        discharge_char="v",
        battery_name=system.get_hostconfig("battery"),
        format="{char}{percent:1.0%}",
    )
    windowtabs_params = default_params(selected=("[", "]"), separator="|")

    graph_defaults = {
        k[0]: k[1]
        for k in [
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
            (
                "start_pos",
                "bottom",
                "Drawer starting position ('bottom'/'top')",
            ),
            ("width", 50, "Width"),
        ]
    }
    cpugraph_params = dict(graph_defaults)
    cpugraph_params["graph_color"] = "FF3333.6"
    cpugraph_params["fill_color"] = "FF3333.3"
    memgraph_params = dict(graph_defaults)
    memgraph_params["graph_color"] = "80FF00.6"
    memgraph_params["fill_color"] = "80FF00.3"
    memgraph_params["type"] = "linefill"
    netgraph_params = dict(graph_defaults)
    sep_params = default_params(padding=4, fontsize=9)  # , size_percent=90)
    graph_label_defaults = dict(
        margin=0,
        padding_x=0,
        padding_y=2,
    )

    # netgraph_params['fill_color'] = "80FF00.3"

    group_splits = (
        (num_groups / num_monitors) if multi_monitor else num_groups,
    )
    # change labels of groups for multi monitor support
    mon_map = {0: {}, 1: {}, 2: {}}
    mon = 0
    for i, group in enumerate(groups):
        if group.name.isdigit():
            if multi_monitor and int(group.name) - 1 in group_splits:
                mon += 1
        groupname = group.name
        grouplabel = group.name[-1] if group.name.isdigit() else group.name
        if group.screen_affinity is None or not multi_monitor:
            mon_map[mon][groupname] = grouplabel
        else:
            mon_map[group.screen_affinity][groupname] = grouplabel

    primary_bar = [
        TextBox("first"),
        Sep(**sep_params),
        # GroupBox(**groupbox_params),
        MultiScreenGroupBox(namemap=mon_map[PRIMARY_SCREEN], **groupbox_params),
        # Sep(**sep_params),
        # Prompt(**prompt_params),
        Sep(**sep_params),
        # TaskList2(**tasklist_params),
        WindowName(**windowname_params),
        # widget.TextBox(**layout_textbox_params),
        Sep(**sep_params),
        CurrentLayout(**current_layout_params),
        # Sep(**sep_params),
        # BitcoinTicker(**bitcointicker_params),
        # Sep(**sep_params),
        # ThreadedPacman(**pacman_params),
        # Sep(**sep_params),
        DF(**default_params()),
        # Sep(**sep_params),
        # BankBalance(account='credit', **default_params()),
        # Sep(**sep_params),
        # BankBalance(account='debit', **default_params()),
        # Sep(**sep_params),
        # PriorityNotify(**default_params()),
        # Image(filename="/usr/share/icons/oxygen/16x16/devices/cpu.png"),
        # Sep(**sep_params),
        # NotmuchCount(**default_params()),
        # Sep(**sep_params),
        # Volume(update_interval=1, **default_params()),
        Sep(**sep_params),
        TextBox(
            "c",
            **default_params(
                foreground=cpugraph_params["graph_color"],
                **graph_label_defaults
            )
        ),
        CPUGraph(**cpugraph_params),
        # Image(filename="/usr/share/icons/oxygen/16x16/devices/media-flash-memory-stick.png"),
        TextBox(
            "m",
            **default_params(
                foreground=memgraph_params["graph_color"],
                **graph_label_defaults
            )
        ),
        MemoryGraph(**memgraph_params),
        # Image(filename="/usr/share/icons/oxygen/16x16/devices/network-wired.png"),
        TextBox(
            "n",
            **default_params(
                foreground=netgraph_params["graph_color"],
                **graph_label_defaults
            )
        ),
        NetGraph(**netgraph_params),
        Sep(**sep_params),
        # Notify(width=30, **notify_params),
        Sep(**sep_params),
    ]
    if system.get_hostconfig("battery"):
        primary_bar.append(Battery(**batteryicon_params))
        primary_bar.append(Sep(**sep_params))

    secondary_bar = [
        TextBox("second"),
        Sep(**sep_params),
        # GroupBox(**groupbox_params),
        MultiScreenGroupBox(
            namemap=mon_map[SECONDARY_SCREEN], **groupbox_params
        ),
        Sep(**sep_params),
        # TaskList2(**tasklist_params),
        WindowName(**windowname_params),
        Sep(**sep_params),
        CurrentLayout(**current_layout_params),
        Sep(**sep_params),
        Systray(**systray_params),
        Sep(**sep_params),
        CalClock(timezone=localtimezone, **clock_params),
    ]
    tertiary_bar = [
        TextBox("third"),
        Sep(**sep_params),
        MultiScreenGroupBox(
            namemap=mon_map[TERTIARY_SCREEN], **groupbox_params
        ),
        # Sep(**sep_params),
        ##TaskList2(**tasklist_params),
        WindowName(**windowname_params),
        Sep(**sep_params),
        CurrentLayout(**current_layout_params),
        CalClock(timezone=localtimezone, **clock_params),
    ]
    quaternary_bar = [
        TextBox("fourth"),
        Sep(**sep_params),
        MultiScreenGroupBox(
            namemap=mon_map[TERTIARY_SCREEN], **groupbox_params
        ),
        # Sep(**sep_params),
        ##TaskList2(**tasklist_params),
        WindowName(**windowname_params),
        Sep(**sep_params),
        CurrentLayout(**current_layout_params),
        CalClock(timezone=localtimezone, **clock_params),
    ]
    bar_defaults = dict(
        focused_background=themes.current_theme.get("focused_background"),
        size=groupbox_params["bar_height"],
        font="Terminus",
        fontsize=12,
    )

    clock_params = default_params(
        padding=2, format="%Y-%m-%d %a %H:%M", fontsize=12
    )
    clock_text = default_params(fontsize=12)

    def make_clock_bar():
        timezones = [
            "UTC",
            "US/Central",
            "Asia/Ho_Chi_Minh",
            "US/Eastern",
            "Australia/Sydney",
            "Asia/Kolkata",
            "Asia/Riyadh",
        ]
        widgets = []
        for timezone in timezones:
            if timezone == localtimezone:
                continue
            widgets.append(TextBox("%s:" % timezone, **clock_text))
            widgets.append(Clock(timezone=timezone, **clock_params))
            widgets.append(
                Sep(**default_params(padding=8, fontsize=9)),
            )
        widgets.extend(
            [
                Sep(**sep_params),
                Pomodoro(**groupbox_params),
            ]
        )
        return Bar(widgets, **bar_defaults)

    # clock_bar.size = 0
    screens = dict()
    if num_monitors == 1:
        primary_bar.append(CalClock(timezone=localtimezone, **clock_params))
        screens[PRIMARY_SCREEN] = Screen(
            Bar(primary_bar, **bar_defaults),
            bottom=make_clock_bar(),
        )
    else:
        screens[PRIMARY_SCREEN] = Screen(
            Bar(primary_bar, **bar_defaults),
            bottom=make_clock_bar(),
        )
        screens[SECONDARY_SCREEN] = Screen(
            Bar(secondary_bar, **bar_defaults),
            bottom=make_clock_bar(),
        )
        screens[TERTIARY_SCREEN] = Screen(
            Bar(tertiary_bar, **bar_defaults),
            bottom=make_clock_bar(),
        )
        screens[QUATERNARY_SCREEN] = Screen(
            Bar(quaternary_bar, **bar_defaults),
            bottom=make_clock_bar(),
        )
    screens = [screens[y] for y in sorted(screens.keys())]
    log.error("Screens: %s ", screens)
    return screens
