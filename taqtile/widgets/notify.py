from libqtile.widget import Notify as QNotify
from libqtile import bar, pangocffi, utils
from libqtile.log_utils import logger
from libqtile.notify import ClosedReason, notifier
from libqtile.widget import base


class Notify(QNotify):
    def __init__(self, width=bar.CALCULATED, **config):
        super().__init__(width=width, **config)
        self.background_normal = self.background
        self.background_urgent = "#710039"

    def calculate_length(self):
        if self.text:
            if self.bar.horizontal:
                return (
                    max(self.layout.width, self.bar.width)
                    + self.actual_padding * 2
                )
            else:
                return (
                    min(self.layout.width, self.bar.height)
                    + self.actual_padding * 2
                )
        else:
            return 0

    def set_notif_text(self, notif):
        # 'actions', 'app_icon', 'app_name', 'body', 'hints', 'id', 'replaces_id', 'summary', 'timeout'
        logger.info("taqtile notifi %s", dir(notif))
        logger.info(f"hints {notif.hints.keys()}, ")
        logger.info(f"hints {notif.hints.get('sender-pid')}, ")
        logger.info(f"hints {notif.app_name}, ")
        logger.info(f"bar {self.bar}, ")
        self.text = pangocffi.markup_escape_text(notif.summary)
        urgency = getattr(notif.hints.get("urgency"), "value", 1)
        if notif.app_name.lower() in ["slack"]:
            urgency = 2

        if urgency != 1:
            self.text = '<span color="%s">%s</span>' % (
                utils.hex(
                    self.foreground_urgent
                    if urgency == 2
                    else self.foreground_low
                ),
                self.text,
            )
            self.background = self.background_urgent
            self.bar.background = self.background
        else:
            self.background = self.background_normal
            self.bar.background = self.background
        if notif.body:
            self.text = '<span weight="bold">%s</span> %s: %s' % (
                notif.app_name,
                self.text,
                pangocffi.markup_escape_text(notif.body),
            )
        if callable(self.parse_text):
            try:
                self.text = self.parse_text(self.text)
            except:  # noqa: E722
                logger.exception("parse_text function failed:")
        if self.audiofile and path.exists(self.audiofile):
            self.qtile.spawn("aplay -q '%s'" % self.audiofile)
        self.text = self.text.replace("\n", " ")
        if len(self.text) > 300:
            self.text = self.text[:300] + "..."
