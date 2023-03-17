from libqtile.widget import base
from libqtile.command import lazy
from functools import wraps

TOGGLE_BUTTON_STATES = {}


class ToggleButton(base._TextBox):
    def __init__(self, name, **config):
        base._TextBox.__init__(self, **config)
        self.name = name
        self.font = "FontAwesome"
        self.add_defaults(
            [
                ("active", False),
                ("active_text", "\uf028 ON"),  # Speaker icon with ON text
                ("inactive_text", "\uf026 OFF"),  # Speaker icon with OFF text
            ]
        )
        self.update_text()

    def _configure(self, qtile, bar):
        global TOGGLE_BUTTON_STATES
        base._TextBox._configure(self, qtile, bar)
        TOGGLE_BUTTON_STATES[self.name] = self.active

    def button_press(self, x, y, button):
        global TOGGLE_BUTTON_STATES
        if button == 1:  # Left mouse button
            self.active = not self.active
            TOGGLE_BUTTON_STATES[self.name] = self.active
            self.update_text()

    def update_text(self):
        self.text = self.active_text if self.active else self.inactive_text
        try:
            self.bar.draw()
        except AttributeError:
            self.draw()


def requires_toggle_button_active(name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            global TOGGLE_BUTTON_STATES
            if TOGGLE_BUTTON_STATES.get(name, False):
                return func(qtile, *args, **kwargs)

        return wrapper

    return decorator
