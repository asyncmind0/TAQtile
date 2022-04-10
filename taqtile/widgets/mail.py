from libqtile.widget import base
from taqtile.log import logger

try:
    import notmuch
except ImportError:
    logger.debug("Notmuch not available")
    notmuch = False
    pass


class NotmuchCount(base.ThreadedPollText):
    def __init__(self, **config):
        base.ThreadedPollText.__init__(self, **config)
        self.query = "(tag:INBOX or tag:inbox) and not (tag:misc or tag:deleted) and date:30d..0s and tag:unread and tag:me"
        self.update_interval = 5

    def poll(self):
        if not notmuch:
            return ""
        db = notmuch.Database()
        query = db.create_query(self.query)
        try:
            count = query.count_messages()
            if count:
                return "\u2709 %s" % count
            else:
                return ""
        except Exception as e:
            logger.exception("Error querying notmuch")
