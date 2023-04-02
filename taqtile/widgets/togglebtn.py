import logging
import subprocess
from libqtile.widget import base
from libqtile.widget.generic_poll_text import GenPollText
from libqtile.command import lazy
from functools import wraps
import shlex
import threading
import time
import logging

logger = logging.getLogger("taqtile")


TOGGLE_BUTTON_STATES = {}


class ToggleButton(GenPollText):
    def __init__(self, name, **config):
        super().__init__(**config)
        self.name = name
        self.font = "FontAwesome"
        self.add_defaults(
            [
                ("active", False),
                ("active_text", "\uf205"),  # use fontawesome
                ("inactive_text", "\uf204"),
                ("on_command", "notify-send switch %(name)s on"),
                ("off_command", "notify-send switch %(name)s off"),
                (
                    "check_state_command",
                    None,
                ),
                (
                    "update_interval",
                    3,
                    "Update interval in seconds, if none, the widget updates only once.",
                ),
                ("func", self.check_state, "Poll Function"),
            ]
        )
        self.check_state()

    def check_state(self):
        global TOGGLE_BUTTON_STATES
        # logger.debug(f"calling {self.check_state_command}")
        # python check status of command string executed in a shell
        if self.check_state_command:

            # Execute the command
            with subprocess.Popen(
                self.check_state_command, shell=True
            ) as process:

                # Wait for the command to complete and get the return code
                return_code = process.wait()
            if return_code == 0:
                self.active = True
            else:
                # logger.debug(f"status {status} {self.check_state_command}")
                self.active = False
        TOGGLE_BUTTON_STATES[self.name] = self.active
        return self.active_text if self.active else self.inactive_text

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
            logger.debug(f"toggle buttons {TOGGLE_BUTTON_STATES}")
            if TOGGLE_BUTTON_STATES.get(name, False):
                return func(*args, **kwargs)

        return wrapper

    return decorator
