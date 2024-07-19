from os.path import expanduser
import json
from taqtile.log import logger

colors = expanduser("~/.cache/wal/colors.json")
colordict = json.load(open(colors))
ColorZ = colordict["colors"]["color0"]
ColorA = colordict["colors"]["color1"]
ColorB = colordict["colors"]["color2"]
ColorC = colordict["colors"]["color3"]
ColorD = colordict["colors"]["color4"]
ColorE = colordict["colors"]["color5"]
ColorF = colordict["colors"]["color6"]
ColorG = colordict["colors"]["color7"]
ColorH = colordict["colors"]["color8"]
ColorI = colordict["colors"]["color9"]

default_theme = dict(
    padding=1,
    margin=0,
    linewidth=4,
    fontsize=14,
    terminal_font="Hack:lcdfilter=lcddefault:hintstyle=hintfull:hinting=true:rgba=rgb:antialias=true:autohint=false",
    terminal_fontsize=18,  #
    font="Hack:lcdfilter=lcddefault:hintstyle=hintfull:hinting=true:rgba=rgb:antialias=true:autohint=false",
    # font="Inconsolata", font="Hack", # font="ProggySquareTTSZ", #
    # font="pango:monospace",
    # font="Terminus",
    borderwidth=1,
    bar_height=20,
    dmenu_lines=30,  #
    # dmenu_command="dmenu -z 1500 -c",
    dmenu_font="Hack-34",
    foreground_urgent="#ffffff",
    background_urgent="#ff007f",
)

# generate a rofi theme matching qtile colors below
star_trek_blue = dict(
    # padding=1,
    border="#5981B9",
    border_focus="#263767",
    # this_current_screen_border="#1C294C",
    # border_focus="#1E90FF",
    border_normal="#0000A0",
    foreground="#06B4E7",
    background="#010F2C",
    # convert to rgba notation
    background_alt="#010F2C",
    hl_foreground="#FFFFFF",
    hl_background="#011846",
    active="#8CC3DF",
    this_current_screen_border="#5981B9",
    highlight_method="block",
    disable_drag=True,
    focused_background="#5981B9",
    focused_foreground="#183d56",
)

matrix_green = dict(
    border="#00FD00",
    border_focus="#00FD00",
    foreground="#00FD00",
    background="#125B29",
    background_alt="#1AF03E",
    hl_foreground="#418200",
    hl_background="#125B29",
    active="#00FD00",
    # highlight_method="block",
    this_current_screen_border="#00FD00",
    bar_height=18,
)

pywal_theme = dict(
    background=ColorZ,
    border_focus=ColorC,
    border_normal=ColorZ,
    foreground=ColorA,
    background_alt=ColorC,
    hl_background=ColorC,
    hl_foreground=ColorG,
    focused_background=ColorI,
    highlight_color=ColorI,
    this_current_screen_border=ColorI,
    highlight_method="block",
)
current_theme = dict(default_theme)
current_theme.update(pywal_theme)
# current_theme.update(star_trek_blue)
# current_theme.update(matrix_green)
logger.debug("Current theme:%s", current_theme)
dmenu_options = (
    "-l %(dmenu_lines)s "
    "-nb '%(background)s' "
    "-nf '%(foreground)s' "
    "-sb %(hl_background)s "
    "-sf %(hl_foreground)s "
    "-fn %(font)s "
)


"""
    "-color-window '%(background)s,%(foreground)s' "
    "-color-normal '%(background)s,%(foreground)s,"
    "%(background_alt)s,%(hl_background)s,%(hl_foreground)s' "
    "-font '%(font)s %(fontsize)s' "
    "-separator-style solid "
    # "-location 1 "
    "-hide-scrollbar "
    "-width 50 "
    # "-monitor -2 "
    "-no-fixed-num-lines "
    "-padding 3 "
    "-line-margin 0 "
"""
rofi_options = ("-i " "-f -bw 1 " "-l 10 ") % current_theme


def dmenu_cmd_args(**overrides):
    opts = dict(current_theme)
    opts.update(overrides)
    # return dmenu_options % opts
    return rofi_options


def default_params(**kwargs):
    de = dict(current_theme)
    de.update(kwargs)
    return de
