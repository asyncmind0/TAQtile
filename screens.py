import logging
import subprocess
import threading

import gobject
from libqtile import bar, widget
from libqtile.widget import graph, base
from libqtile.config import Screen

import system
import themes
from multiscreengroupbox import MultiScreenGroupBox
from priority_notify import PriorityNotify
from bank import CommBank

log = logging.getLogger('qtile')

PRIMARY_SCREEN = system.get_screen(0)
SECONDARY_SCREEN = system.get_screen(1)


class ThreadedPacman(widget.Pacman):

    def __init__(self, *args, **kwargs):
        super(ThreadedPacman, self).__init__(*args, **kwargs)
        self.timeout_add(self.update_interval, self.wx_updater)
        self.wx_updater()

    def update(self, data=None):
        if self.configured and data:
            self.updates_data = str(data)
            if self.text != self.updates_data:
                self.text = self.updates_data
                self.bar.draw()
        return "N/A"

    def wx_updater(self):
        log.warn('adding WX Pacman widget timer')

        def worker():
            pacman = subprocess.Popen(['checkupdates'], stdout=subprocess.PIPE)
            data = len(pacman.stdout.readlines())
            gobject.idle_add(self.update, data)
        threading.Thread(target=worker).start()
        return True


class BankBalance(base.ThreadedPollText):
    defaults = [
        ('warning', 'FF0000', 'Warning Color - no updates.'),
        ('unavailable', 'ffffff', 'Unavailable Color - no updates.'),
        ("account", "all", "Which account to show (all/0/1/2/...)"),
    ]
    fixed_upper_bound = False

    def __init__(self, **config):
        # graph._Graph.__init__(self, **config)
        base.ThreadedPollText.__init__(self, **config)
        self.add_defaults(BankBalance.defaults)

    def draw(self):
        try:
            if float(self.text) <= 0:
                self.layout.colour = self.warning
            else:
                self.layout.colour = self.foreground
        except Exception as e:
            log.exception("Draw error")
        base.ThreadedPollText.draw(self)

    def poll(self, data=None):
        text = "$$$$"
        try:
            user = subprocess.check_output(
                ['pass', "financial/commbank/debit/user"]).strip()
            password = subprocess.check_output(
                ['pass', "financial/commbank/debit/pass"]).strip()
            log.warning("BankBalance:%s", user)
            commbank = CommBank(user, password)
            self.data = data = commbank.data
            text = commbank.get_currency(
                commbank.data['AccountGroups'][0]['ListAccount'][-2]['AvailableFunds']
            )
            log.warning("BankBalance:%s", text)
        except Exception as e:
            log.exception("BankBalance: %s %s", user, data)
        # text = commbank.net_position
        return str(text)


class CalClock(widget.Clock):
    # def button_release(self, x, y, button):

    def button_press(self, x, y, button):
        self.qtile.cmd_spawn("calendar_applet.py")


class GraphHistory(widget.NetGraph):
    """Graph that persists history and reloads it when restarted.
    provides a continuous graph, desipite qtile restarting.
    """
    default_store = None

    def __init__(self, *args, **kwargs):
        super(widget.NetGraph, self).__init__(*args, **kwargs)

    def push(self, value):
        return super(widget.NetGraph, self).push(value)


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
        highlight_method='block',
        padding=-1,
        this_current_screen_border=themes.current_theme['border'])

    prompt_params = default_params()
    systray_params = default_params()
    current_layout_params = default_params(
        name="default", padding=2)
    #windowname_params = default_params
    systray_params = default_params()
    clock_params = default_params(padding=2, fmt='%Y-%m-%d %a %H:%M')
    pacman_params = default_params()
    notify_params = default_params()
    bitcointicker_params = default_params()
    batteryicon_params = default_params()
    batteryicon_params['battery_name'] = "BAT1"
    batteryicon_params['format'] = "{percent:5.0%}"
    windowtabs_params = default_params(selected=("[", "]"))
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
        MultiScreenGroupBox(
            namemap=mon_map[PRIMARY_SCREEN], **groupbox_params),
        widget.Sep(**sep_params),
        widget.Prompt(**prompt_params),
        widget.Sep(**sep_params),
        widget.WindowTabs(**windowtabs_params),
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
        MultiScreenGroupBox(
            namemap=mon_map[SECONDARY_SCREEN], **groupbox_params),
        widget.Sep(**sep_params),
        widget.WindowTabs(**windowtabs_params),
        widget.Sep(**sep_params),
        widget.CurrentLayout(**current_layout_params),
        widget.Sep(**sep_params),
        CalClock(**clock_params),
    ]
    bar_map = {PRIMARY_SCREEN: primary_bar, SECONDARY_SCREEN: secondary_bar}
    bar_height = groupbox_params.get('bar_height', 10)
    screens.append(Screen(bar.Bar(bar_map[PRIMARY_SCREEN], bar_height)))
    if num_monitors > 1:
        screens.append(Screen(bar.Bar(bar_map[SECONDARY_SCREEN], bar_height)))
    return screens
