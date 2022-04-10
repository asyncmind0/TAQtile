from libqtile.bar import Bar as QBar
from taqtile.themes import current_theme, default_params

from taqtile.log import logger


class Bar(QBar):
    default_background = None
    defaults = [
        ("focused_background", "#FF0000", "Background colour."),
    ]

    def __init__(self, widgets, **config):
        bar_defaults = default_params(
            focused_background=current_theme.get("focused_background"),
        )
        bar_defaults.update(config)
        super().__init__(
            widgets, current_theme.get("bar_height", 8), **bar_defaults
        )
        self.add_defaults(Bar.defaults)
        self.default_background = self.background

    def _configure(self, qtile, screen, reconfigure=False):
        self.default_background = self.background
        return super()._configure(qtile, screen, reconfigure=reconfigure)

    def draw(self):
        # logger.debug("Current screen %s", self.qtile.current_screen.index)
        # logger.debug("Bar screen %s", self.screen.index)
        # logger.debug(
        #    "Background %s %s", self.background, self.focused_background
        # )
        if self.qtile.current_screen.index == self.screen.index:
            # logger.debug("Bar is focused screen %s", self.screen.index)
            self.background = self.focused_background
        else:
            self.background = self.default_background
        return super().draw()
