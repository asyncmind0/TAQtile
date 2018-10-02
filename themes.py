from log import logger


default_theme = dict(
    padding=1,
    margin=0,
    linewidth=1,
    fontsize=12,
    font="Inconsolata",
    #font="Terminus",
    #font="ProggySquareTTSZ",
    #font="pango:monospace",
    borderwidth=1,
    bar_height=16
)

star_trek_blue = dict(
    border="#5981B9",
    border_focus="#263767",
    #this_current_screen_border="#1C294C",
    #border_focus="#1E90FF",
    border_normal="#0000A0",
    foreground="#06B4E7",
    background="#010F2C",
    background_alt="#010F2C",
    hl_foreground="#FFFFFF",
    hl_background="#011846",
    active="#8CC3DF",
    this_current_screen_border="#5981B9",
    highlight_method="block",
    disable_drag=True,
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
    #highlight_method="block",
    this_current_screen_border="#00FD00",
    bar_height=18
)

current_theme = dict(default_theme)
current_theme.update(star_trek_blue)
#current_theme.update(matrix_green)
logger.debug("Current theme:%s", current_theme)
#current_theme = matrix_green
#dmenu_defaults = (
#    "-w -f -l 40 "
#    "-nb black -nf white "
#    "-sb %(background)s -sf %(foreground)s "
#    "-fn %(font)s"
#) % current_theme

#dmenu_defaults = (
#    "-w -f -l 40 "
#    "-nb #000000 -nf #FFFFFF "
#    "-bg #000000 -fg %(foreground)s "
#    "-font '%(font)s %(fontsize)s' "
#    "-bgalt '#001400' "
#    "-location 1 "
#) % current_theme

rofi_defaults = (
    "-f -l 10 -bw 1 "
    "-separator-style solid "
    "-color-window '%(background)s,%(foreground)s' "
    "-color-normal '%(background)s,%(foreground)s,"
    "%(background_alt)s,%(hl_background)s,%(hl_foreground)s' "
    "-font '%(font)s %(fontsize)s' "
    #"-location 1 "
    "-hide-scrollbar "
    "-width 50 "
    "-monitor -2 "
) % current_theme

def dmenu_defaults():
    return rofi_defaults
