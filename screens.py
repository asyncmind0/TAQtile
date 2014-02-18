from libqtile.config import Key, Click, Drag, Screen, Group, Match, Rule
from libqtile.command import lazy
from libqtile import layout, bar, widget, hook
from themes import current_theme
from multiscreengroupbox import MultiScreenGroupBox
import logging
import system
import gobject
import threading
import subprocess
log = logging.getLogger("qtile.screen")
log.setLevel(logging.DEBUG)


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

#Pacman = widget.Pacman
Pacman = ThreadedPacman
#GroupBox = widget.GroupBox
GroupBox = MultiScreenGroupBox


def get_screens(num_screens=1):
    screens = []

    def default_params(**kwargs):
        de = dict(
            font=current_theme['font'],
            fontsize=10,
            padding=1,
            borderwidth=1,
        )
        de.update(kwargs)
        return de

    groupbox_params = default_params(
        urgent_alert_method='text',
        padding=1,
        borderwidth=1,
        rounded=False,
        highlight_method='block',
        this_current_screen_border=current_theme['border'])

    prompt_params = default_params()
    systray_params = default_params()
    layout_textbox_params = default_params(name="default", text="default config")
    layout_textbox_params['padding'] = 2
    #windowname_params = default_params
    systray_params = default_params()
    clock_params = default_params(fmt='%Y-%m-%d %a %H:%M')
    pacman_params = default_params()
    notify_params = default_params()
    bitcointicker_params = default_params()
    batteryicon_params = default_params()
    batteryicon_params['battery_name'] = "BAT1"
    batteryicon_params['format'] = "{percent:5.0%}"
    current_layout_params = default_params(foreground=current_theme['foreground'])
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
    #netgraph_params['fill_color'] = "80FF00.3"

    gb1 = dict([(str(i), str(i)) for i in range(1, 10)])
    gb2 = dict([(str(i), str(i-10)) for i in range(11, 20)])
    if num_screens == 1:
        gb1['right'] = "term1"
        gb1['left'] = "term2"
    else:
        # if primary and seconday are reversed
        if PRIMARY_SCREEN:
            gb1['right'] = "term"
            gb2['left'] = "term"
        else:
            gb1['left'] = "term"
            gb2['right'] = "term"

    w1 = [
        GroupBox(namemap=gb1, **groupbox_params),
        widget.Sep(),
        widget.Prompt(**prompt_params),
        widget.Sep(),
        widget.WindowTabs(**windowtabs_params),
        #widget.WindowName(**windowname_params),
        #widget.TextBox(**layout_textbox_params),
        widget.Sep(),
        widget.CurrentLayout(**current_layout_params),
        widget.Sep(),
        #widget.BitcoinTicker(**bitcointicker_params),
        #widget.Sep(),
        #Pacman(**pacman_params),
        widget.DF(),
        #widget.Image(filename="/usr/share/icons/oxygen/16x16/devices/cpu.png"),
        widget.CPUGraph(**cpugraph_params),
        #widget.Image(filename="/usr/share/icons/oxygen/16x16/devices/media-flash-memory-stick.png"),
        widget.MemoryGraph(**memgraph_params),
        #widget.Image(filename="/usr/share/icons/oxygen/16x16/devices/network-wired.png"),
        widget.NetGraph(**netgraph_params),
        widget.Sep(),
        widget.Notify(**notify_params),
        widget.Sep()
    ]
    if system.get_hostconfig('battery'):
        w1.append(widget.Battery(**batteryicon_params))
        w1.append(widget.Sep())
    w1.append(widget.Systray(**systray_params))
    w1.append(widget.Clock(**clock_params))

    w2 = [
        GroupBox(namemap=gb2, **groupbox_params),
        widget.Sep(),
        widget.WindowTabs(**windowtabs_params),
        widget.Sep(),
        widget.CurrentLayout(**current_layout_params),
        widget.Sep(),
        widget.Clock(**clock_params),
    ]

    screens.append(Screen(bar.Bar(w1, 18)))
    if num_screens > 1:
        screens.append(Screen(bar.Bar(w2, 18)))
    return screens
