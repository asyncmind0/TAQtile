from libqtile.config import Key, Click, Drag, Screen, Group, Match, Rule
from libqtile.command import lazy
from libqtile import layout, bar, widget, hook
import themes
from multiscreengroupbox import MultiScreenGroupBox
from priority_notify import PriorityNotify
import logging as log
import system
import gobject
import threading
import subprocess


PRIMARY_SCREEN = system.get_screen(0)
SECONDARY_SCREEN = system.get_screen(1)


class ThreadedPacman(widget.Pacman):
    def __init__(self, *args, **kwargs):
        super(ThreadedPacman, self).__init__(*args, **kwargs)
        self.timeout_add(self.interval, self.wx_updater)
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


class CalClock(widget.Clock):
    #def button_release(self, x, y, button):
    def button_press(self, x, y, button):
        self.qtile.cmd_spawn("calendar_applet.py")


class GraphHistory(widget.NetGraph):
    default_store=None
    def __init__(self, *args, **kwargs):
        super(widget.NetGraph, self).__init__(*args, **kwargs)

    def push(self, value):
        return super(widget.NetGraph, self).push(value)

#Pacman = widget.Pacman
Pacman = ThreadedPacman
#GroupBox = widget.GroupBox
GroupBox = MultiScreenGroupBox


def get_screens(num_monitors=1):

    screens = []

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
    current_layout_params= default_params(
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
    #netgraph_params['fill_color'] = "80FF00.3"

    gb1 = dict([(str(i), str(i)) for i in range(1, 10)])
    gb2 = dict([(str(i), str(i-10)) for i in range(11, 20)])
    if num_monitors == 1:
        gb1['right'] = "term1"
        gb1['left'] = "term2"
        gb1['remote_right'] = "remote_term1"
        gb1['remote_left'] = "remote_term2"
        gb1['monitor'] = "monitor"
    else:
        # if primary and seconday are reversed
        if PRIMARY_SCREEN:
            gb1['right'] = "term"
            gb2['left'] = "term"
            gb1['remote_right'] = "remote_term"
            gb2['remote_left'] = "remote_term"
        else:
            gb1['left'] = "term"
            gb2['right'] = "term"
            gb1['remote_left'] = "remote_term"
            gb2['monitor'] = "monitor"
            gb2['remote_right'] = "remote_term"
    gb1['comm'] = "comm"
    gb1['mail'] = "mail"

    w1 = [
        GroupBox(namemap=gb1, **groupbox_params),
        widget.Sep(**sep_params),
        widget.Prompt(**prompt_params),
        widget.Sep(**sep_params),
        widget.WindowTabs(**windowtabs_params),
        #widget.WindowName(**windowname_params),
        #widget.TextBox(**layout_textbox_params),
        widget.Sep(**sep_params),
        widget.CurrentLayout(**current_layout_params),
        widget.Sep(**sep_params),
        #widget.BitcoinTicker(**bitcointicker_params),
        #widget.Sep(**sep_params),
        #Pacman(**pacman_params),
        widget.DF(**default_params()),
        PriorityNotify(**default_params()),
        #widget.Image(filename="/usr/share/icons/oxygen/16x16/devices/cpu.png"),
        widget.TextBox("c:", **default_params()),
        widget.CPUGraph(**cpugraph_params),
        #widget.Image(filename="/usr/share/icons/oxygen/16x16/devices/media-flash-memory-stick.png"),
        widget.TextBox("m:", **default_params()),
        widget.MemoryGraph(**memgraph_params),
        #widget.Image(filename="/usr/share/icons/oxygen/16x16/devices/network-wired.png"),
        widget.TextBox("n:", **default_params()),
        widget.NetGraph(**netgraph_params),
        #widget.Sep(**sep_params),
        #widget.Notify(width=30, **notify_params),
        widget.Sep(**sep_params)
    ]
    if system.get_hostconfig('battery'):
        w1.append(widget.Battery(**batteryicon_params))
        w1.append(widget.Sep(**sep_params))
    w1.append(widget.Systray(**systray_params))
    w1.append(CalClock(**clock_params))

    w2 = [
        GroupBox(namemap=gb2, **groupbox_params),
        widget.Sep(**sep_params),
        widget.WindowTabs(**windowtabs_params),
        widget.Sep(**sep_params),
        widget.CurrentLayout(**current_layout_params),
        widget.Sep(**sep_params),
        CalClock(**clock_params),
    ]
    bar_height = groupbox_params.get('bar_height', 10)
    screens.append(Screen(bar.Bar(w1, bar_height)))
    if num_monitors > 1:
        screens.append(Screen(bar.Bar(w2, bar_height)))
    return screens
