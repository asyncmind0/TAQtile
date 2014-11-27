import logging as log


default_theme = dict(
    fontsize=14,
    padding=0,
    font="Inconsolata",
    borderwidth=2,
    bar_height=18
)

star_trek_blue = dict(
    border="#00FFDD",
    border_focus="#1E90FF",
    border_normal="#0000A0",
    border_width=2,
    foreground="#06B4E7",
    background="#010F2C",
)

matrix_green = dict(
    border="#1AF03E",
    border_focus="#1AF03E",
    foreground="#00FD00",
    background="#125B29",
    borderwidth=2,
    bar_height=18
)

current_theme = dict(default_theme)
current_theme.update(star_trek_blue)
log.debug("Current theme:%s", current_theme)
#current_theme = matrix_green
dmenu_defaults = (
    "-w -f -l 40 "
    "-nb black -nf white "
    "-sb '%(background)s' -sf '%(foreground)s' "
    "-fn %(font)s"
) % current_theme
