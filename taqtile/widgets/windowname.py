from libqtile.widget import WindowName as QWindowName

from taqtile.log import logger
from libqtile import bar, hook, pangocffi


class WindowName(QWindowName):
    default_background = None
    defaults = [
        ("focused_background", "#FF0000", "Focused background colour."),
        ("focused_foreground", "#000000", "Focused foreground colour."),
        ("use_mouse_wheel", True, "Whether to use mouse wheel events"),
        (
            "invert_mouse_wheel",
            False,
            "Whether to invert mouse wheel group movement",
        ),
    ]

    def __init__(self, **config):
        super().__init__(**config)
        self.add_defaults(WindowName.defaults)
        self.default_background = self.background
        self.default_foreground = self.foreground
        default_callbacks = {}
        if self.use_mouse_wheel:
            default_callbacks.update(
                {
                    "Button5"
                    if self.invert_mouse_wheel
                    else "Button4": self.prev_window,
                    "Button4"
                    if self.invert_mouse_wheel
                    else "Button5": self.next_window,
                }
            )
        self.add_callbacks(default_callbacks)

    def next_window(self):
        self.qtile.current_group.next_window()

    def prev_window(self):
        self.qtile.current_group.prev_window()

    def _configure(self, qtile, bar):
        super()._configure(qtile, bar)
        hook.subscribe.current_screen_change(self.hook_response)

    def draw(self):
        if self.bar.screen == self.qtile.current_screen:
            self.background = self.focused_background
            self.foreground = self.focused_foreground
        else:
            self.background = self.default_background
            self.foreground = self.default_foreground
        return super().draw()
