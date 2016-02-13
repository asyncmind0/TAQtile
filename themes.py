import logging as log


default_theme = dict(
    fontsize=14,
    padding=0,
    font="Inconsolata",
    #font="Terminus",
    borderwidth=1,
    bar_height=20
)

star_trek_blue = dict(
    border="#5981B9",
    border_focus="#263767",
    #this_current_screen_border="#1C294C",
    #border_focus="#1E90FF",
    border_normal="#0000A0",
    foreground="#06B4E7",
    background="#010F2C",
    active="#8CC3DF",
    this_current_screen_border="#5981B9",
    highlight_method="block",
    disable_drag=True,
)

matrix_green = dict(
    border="#1AF03E",
    border_focus="#1AF03E",
    foreground="#00FD00",
    background="#125B29",
    active="#00FD00",
    this_current_screen_border="#1AF03E",
    bar_height=18
)

current_theme = dict(default_theme)
#current_theme.update(star_trek_blue)
current_theme.update(matrix_green)
log.debug("Current theme:%s", current_theme)
#current_theme = matrix_green
#dmenu_defaults = (
#    "-w -f -l 40 "
#    "-nb black -nf white "
#    "-sb %(background)s -sf %(foreground)s "
#    "-fn %(font)s"
#) % current_theme

dmenu_defaults = (
    "-w -f -l 40 "
    "-nb black -nf white "
    "-bg black -fg %(foreground)s "
    "-font '%(font)s %(fontsize)s' "
    "-bgalt '#001400' "
    "-location 1 "
) % current_theme
