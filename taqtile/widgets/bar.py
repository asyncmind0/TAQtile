import logging
from libqtile.bar import Bar as QBar
from libqtile import bar, hook, pangocffi
from libqtile.widget import base

logger = logging.getLogger("taqtile")


class Bar(QBar):
    default_background = None
    defaults = [
        ("focused_background", "#000000", "Background colour."),
    ]

    def __init__(self, widgets, **config):
        bar_height = config.pop("bar_height", 8) or 8
        super().__init__(widgets, int(bar_height), **config)
        self.add_defaults(Bar.defaults)
        self.default_background = self.background
        self.default_foreground = self.foreground
        hook.subscribe.current_screen_change(self._hook_current_screen_change)

    def _hook_current_screen_change(self, *args):
        if not self.qtile:
            return
        logger.debug(
            f"current_screen_change current_screen: {self.qtile.current_screen.index} self.screen:{self.screen.index}"
        )

        if self.screen == self.qtile.current_screen:
            self.background = self.focused_background
        else:
            self.background = self.default_background
        try:
            self._configure(self.qtile, self.screen, reconfigure=True)
        except Exception as e:
            logger.error(f"Error configuring Bar {self}")
        self.draw()


class Spacer(base._Widget):
    """Just an empty space on the bar

    Often used with length equal to bar.STRETCH to push bar widgets to the
    right or bottom edge of the screen.

    Parameters
    ==========
    length :
        Length of the widget.  Can be either ``bar.STRETCH`` or a length in
        pixels.
    width :
        DEPRECATED, same as ``length``.
    """

    orientations = base.ORIENTATION_BOTH
    defaults = [
        ("background", None, "Widget background color"),
        ("focused_background", "#000000", "Background colour."),
    ]

    def __init__(self, length=bar.STRETCH, **config):
        """ """
        base._Widget.__init__(self, length, **config)
        self.add_defaults(Spacer.defaults)
        self.default_background = self.background
        hook.subscribe.current_screen_change(self._hook_current_screen_change)

    def _hook_current_screen_change(self, *args):
        if not self.qtile:
            return
        logger.debug(
            f"current_screen_change current_screen: {self.qtile.current_screen.index} self.bar.screen:{self.bar.screen.index}"
        )

        if self.bar.screen == self.qtile.current_screen:
            self.background = self.focused_background
        else:
            self.background = self.default_background
        self._configure(self.qtile, self.bar)
        self.draw()

    def draw(self):
        if self.length > 0:
            self.drawer.clear(self.background or self.bar.background)
            if self.bar.horizontal:
                self.drawer.draw(
                    offsetx=self.offset, offsety=self.offsety, width=self.length
                )
            else:
                self.drawer.draw(
                    offsety=self.offset,
                    offsetx=self.offsetx,
                    height=self.length,
                )
