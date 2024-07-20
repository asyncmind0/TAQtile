from libqtile import bar, hook
from typing import Any
from libqtile.widget import GenPollText
import logging
from datetime import datetime

import psutil

logger = logging.getLogger(__name__)

NOAUTOCLOSE = []
REAP_INCLUDE_PATTERNS = []


class WindowCleaner(GenPollText):
    defaults: list[tuple[str, Any, str]] = [
        ("font", "sans", "Text font"),
        ("fontsize", None, "Font pixel size. Calculated if None."),
        ("fontshadow", None, "font shadow color, default is None(no shadow)"),
        ("padding", None, "Padding left and right. Calculated if None."),
        ("foreground", "#ffffff", "Foreground colour."),
        ("text_format", "{num}", "Format for message"),
        ("show_zero", False, "Show window count when no windows"),
        ("no_autoclose", [], "Windows patterns that should not be closed"),
        ("include_patterns", [], "Window Patterns  that should be autoclosed"),
    ]

    def __init__(self, width=bar.CALCULATED, **config):
        GenPollText.__init__(self, width=width, **config)
        self.add_defaults(WindowCleaner.defaults)
        self._count = 0

    def func(self):
        logger.info("Cleaner called")
        close_old_windows()
        return self.text

    def _setup_hooks(self):
        hook.subscribe.client_killed(self._win_killed)
        hook.subscribe.client_managed(self._wincount)
        hook.subscribe.current_screen_change(self._wincount)
        hook.subscribe.setgroup(self._wincount)

    def _wincount(self, *args):
        try:
            self._count = len(self.bar.screen.group.windows)
        except AttributeError:
            self._count = 0

        self.update(self.text_format.format(num=self._count))

    def _win_killed(self, window):
        try:
            self._count = len(self.bar.screen.group.windows)
        except AttributeError:
            self._count = 0

        self.update(self.text_format.format(num=self._count))


def close_old_windows():
    from libqtile import qtile

    logger.debug("checking for windows to reap")

    for key, win in list(qtile.windows_map.items()):
        proc = psutil.Process(win.get_pid())
        created = datetime.fromtimestamp(proc.create_time())
        try:
            if (
                win.get_wm_class() != "qutebrowser"
                or win.get_wm_class() != "brave"
            ):
                continue
            if (datetime.now() - created) > timedelta(days=1):
                for pattern in REAP_INCLUDE_PATTERNS:
                    if not re.match(pattern, win.name):
                        continue
                if key not in NOAUTOCLOSE:
                    logger.error(
                        f"Old window found marked for kill: {key}:{win.name} {win.get_wm_class()}{(datetime.now() - created) > timedelta(days=1)}"
                    )
        except AttributeError:
            pass
        except:
            logger.exception("Error reaping windows")
