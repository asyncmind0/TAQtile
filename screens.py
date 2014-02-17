from libqtile.config import Key, Click, Drag, Screen, Group, Match, Rule
from libqtile.command import lazy
from libqtile import layout, bar, widget, hook
from themes import current_theme
import logging
import system
import gobject
import threading
import subprocess
log = logging.getLogger("qtile.screen")
log.setLevel(logging.DEBUG)
try:
    from metrics_widget import Metrics
except Exception as e:
    log.exception(e)


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


class MultiScreenGroupBox(widget.GroupBox):
    def __init__(self, **config):
        widget.GroupBox.__init__(self, **config)
        self.namemap = config.get('namemap', {})

    def draw(self):
        self.drawer.clear(self.background or self.bar.background)

        offset = 0
        for i, g in enumerate(self.qtile.groups):
            gtext = g.name
            #log.debug(gtext)
            if gtext in self.namemap:
                gtext = self.namemap[gtext]
            else:
                continue

            is_block = (self.highlight_method == 'block')

            bw = self.box_width([g])
            if g.screen:
                if self.bar.screen.group.name == g.name:
                    if self.qtile.currentScreen == self.bar.screen:
                        border = self.this_current_screen_border
                    else:
                        border = self.this_screen_border
                else:
                    border = self.other_screen_border
            elif self.group_has_urgent(g) and \
                    self.urgent_alert_method in ('border', 'block'):
                border = self.urgent_border
                if self.urgent_alert_method == 'block':
                    is_block = True
            else:
                border = self.background or self.bar.background

            if self.group_has_urgent(g) and self.urgent_alert_method == "text":
                text = self.urgent_text
            elif g.windows:
                text = self.active
            else:
                text = self.inactive

            self.drawbox(
                self.margin_x + offset,
                gtext,
                border,
                text,
                self.rounded,
                is_block,
                bw - self.margin_x * 2 - self.padding_x * 2
            )
            offset += bw
        self.drawer.draw(self.offset, self.width)

#GroupBox = widget.GroupBox
GroupBox = MultiScreenGroupBox


def get_screens(num_screens=1):
    screens = []
    default_params = dict(
        font=current_theme['font'],
        fontsize=10,
        padding=1,
        borderwidth=1,
    )

    groupbox_params = dict(
        urgent_alert_method='text',
        padding=1,
        borderwidth=1,
        rounded=False,
        highlight_method='block',
        this_current_screen_border=current_theme['border'])

    groupbox_params.update(default_params)
    prompt_params = default_params
    systray_params = default_params
    layout_textbox_params = dict(name="default", text="default config")
    layout_textbox_params.update(default_params)
    layout_textbox_params['padding'] = 2
    #windowname_params = default_params
    systray_params = default_params
    clock_params = dict(fmt='%Y-%m-%d %a %H:%M')
    clock_params.update(default_params)
    pacman_params = default_params
    notify_params = default_params
    bitcointicker_params = default_params
    batteryicon_params = default_params
    batteryicon_params['battery_name'] = "BAT1"
    batteryicon_params['format'] = "{percent:5.0%}"
    current_layout_params = dict(foreground=current_theme['foreground'])
    current_layout_params.update(default_params)
    windowtabs_params = dict(selected=("[", "]"))
    windowtabs_params.update(default_params)
    graph_defaults = {k[0]: k[1] for k in[
        ("graph_color", "18BAEB", "Graph color"),
        ("fill_color", "1667EB.3", "Fill color for linefill graph"),
        ("border_color", "215578", "Widget border color"),
        ("border_width", 1, "Widget border width"),
        ("margin_x", 1, "Margin X"),
        ("margin_y", 1, "Margin Y"),
        ("samples", 100, "Count of graph samples."),
        ("frequency", 1, "Update frequency in seconds"),
        ("type", "line", "'box', 'line', 'linefill'"),
        ("line_width", 1, "Line width"),
        ("start_pos", "bottom", "Drawer starting position ('bottom'/'top')"),
        ("width", 50, "Width")
    ]}
    cpugraph_params = graph_defaults
    memgraph_params = graph_defaults
    netgraph_params = graph_defaults

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
        widget.CPUGraph(**cpugraph_params),
        widget.MemoryGraph(**memgraph_params),
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
