import logging
import subprocess
from functools import wraps
from libqtile import hook

from libqtile.widget.generic_poll_text import GenPollText
from libqtile.widget.image import Image
from qtile_extras.widget.mixins import TooltipMixin
from libqtile.lazy import lazy
from libqtile import qtile




logger = logging.getLogger("taqtile")


TOGGLE_BUTTON_STATES = {}

class Button(Image, TooltipMixin):
    foreground = None
    defaults = [
        ("foreground", True, "Enable/Disable image scaling"),
        ]
    def __init__(self, name, **config):
        Image.__init__(self, **config)
        TooltipMixin.__init__(self, **config)
        self.name = name
        self.font = "FontAwesome"
        self.add_defaults(
            [
                ("active", False),
                ("active_text", "\uf205"),  # use fontawesome
                ("active_background", None),  # use fontawesome
                ("inactive_text", "\uf204"),
                ("inactive_background", None),  # use fontawesome
                ("command", "notify-send button pushed %(name)s on"),
            ]
            + TooltipMixin.defaults
        )
        self.tooltip_text = self.name

class CloseButton(Button):
    def __init__(self, **config):
        Button.__init__(self,"close", filename="/usr/share/icons/breeze/actions/16/window-close.svg")
        self.add_callbacks({"Button1": self.do_close})
    def do_close(self):
        logger.info(f"closing window {self.bar.window}")
        qtile.current_window.kill()
        


class ToggleButton(GenPollText, TooltipMixin):
    def __init__(self, name, **config):
        GenPollText.__init__(self, **config)
        TooltipMixin.__init__(self, **config)
        self.name = name
        self.font = "FontAwesome"
        self.add_defaults(
            [
                ("active", False),
                ("active_text", "\uf205"),  # use fontawesome
                ("active_background", None),  # use fontawesome
                ("inactive_text", "\uf204"),
                ("inactive_background", None),  # use fontawesome
                ("on_command", "notify-send switch %(name)s on"),
                ("off_command", "notify-send switch %(name)s off"),
                (
                    "check_state_command",
                    None,
                ),
                (
                    "update_interval",
                    5,
                    "Update interval in seconds, if none, the widget updates only once.",
                ),
                ("func", self.check_state, "Poll Function"),
                ("focused_background", "#ffffff", "Background colour."),
                ("focused_foreground", "#000000", "Background colour."),
            ]
            + TooltipMixin.defaults
        )
        self.tooltip_text = self.name
        self.default_background = self.background
        self.check_state()
        self.default_background = self.background
        self.default_foreground = self.foreground
        hook.subscribe.current_screen_change(self._hook_current_screen_change)

    def _hook_current_screen_change(self, *args):
        if not getattr(self, "qtile", None):
            return
        logger.debug(
            f"current_screen_change current_screen: {self.qtile.current_screen.index} self.bar.screen:{self.bar.screen.index}"
        )

        if self.bar.screen == self.qtile.current_screen:
            self.background = self.focused_background
            self.foreground = self.focused_foreground
        else:
            self.background = self.default_background
            self.foreground = self.default_foreground
        try:
            self._configure(self.qtile, self.bar)
        except Exception as e:
            logger.error(f"Error configuring ToggleButton {self.name}")
        self.draw()

    def _update_background(self):
        self.background = (
            self.active_background
            if self.active
            else (self.inactive_background or self.default_background)
        )

    def check_state(self):
        try:
            global TOGGLE_BUTTON_STATES
            # logger.debug(f"calling {self.check_state_command}")
            # python check status of command string executed in a shell
            if self.check_state_command:
                # Execute the command
                with subprocess.Popen(
                    self.check_state_command,
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                ) as process:
                    # Wait for the command to complete and get the return code
                    return_code = process.wait()
                if return_code == 0:
                    self.active = True
                else:
                    # logger.debug(f"status {status} {self.check_state_command}")
                    self.active = False
            TOGGLE_BUTTON_STATES[self.name] = self.active
            self._update_background()
            return self.active_text if self.active else self.inactive_text
        except Exception as e:
            logger.exception("failed to check state")

    def _configure(self, qtile, bar):
        global TOGGLE_BUTTON_STATES
        super()._configure(qtile, bar)
        TOGGLE_BUTTON_STATES[self.name] = self.active

    def button_press(self, x, y, button):
        global TOGGLE_BUTTON_STATES
        if button == 1:  # Left mouse button
            self.active = not self.active
            TOGGLE_BUTTON_STATES[self.name] = self.active
            self.execute()
        self.update_text()

    def execute(self):
        if self.active:
            self.qtile.spawn(self.on_command)
        else:
            self.qtile.spawn(self.off_command)

    def update_text(self):
        self.text = str(self.active_text if self.active else self.inactive_text)
        try:
            self.bar.draw()
        except AttributeError:
            self.draw()


def requires_toggle_button_active(name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            global TOGGLE_BUTTON_STATES
            # logger.debug(f"toggle buttons {TOGGLE_BUTTON_STATES}")
            if TOGGLE_BUTTON_STATES.get(name, False):
                return func(*args, **kwargs)

        return wrapper

    return decorator
