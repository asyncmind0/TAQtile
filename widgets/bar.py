from libqtile.bar import Bar as QBar

from log import logger


class Bar(QBar):
    default_background = None
    defaults = [
        ("focused_background", "#FF0000", "Background colour."),
    ]
    def __init__(self, widgets, size, **config):
        super().__init__(widgets, size, **config)
        self.add_defaults(Bar.defaults)
        self.default_background = self.background
    def _configure(self, qtile, screen):
        self.default_background = self.background
        return super()._configure(qtile, screen)
    def _actual_draw(self):
        logger.debug("Current screen %s", self.qtile.current_screen.index)
        logger.debug("Bar screen %s", self.screen.index)
        logger.debug("Background %s %s", self.background, self.focused_background)
        if self.qtile.current_screen.index == self.screen.index:
            self.background = self.focused_background
        else:
            self.background = self.default_background
        return super()._actual_draw()
