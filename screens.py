from libqtile.config import Key, Click, Drag, Screen, Group, Match, Rule
from libqtile.command import lazy
from libqtile import layout, bar, widget, hook


def get_screens():
    common_widgets1 = [
            widget.GroupBox(),
            widget.Prompt(),
            widget.WindowName(),
            widget.TextBox("default config", name="default"),
            widget.Systray(),
            widget.Clock('%Y-%m-%d %a %I:%M %p'),
        ]
    common_widgets2 = [
            widget.GroupBox(),
            widget.Prompt(),
            widget.WindowName(),
            widget.TextBox("default config", name="default"),
            widget.Systray(),
            widget.Clock('%Y-%m-%d %a %I:%M %p'),
        ]
    tbar = bar.Bar(common_widgets1, 30)
    return [Screen(top=tbar),
            Screen(top=bar.Bar(common_widgets2, 30))]
