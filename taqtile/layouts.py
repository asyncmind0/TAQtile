import logging
from libqtile.layout.max import Max as QMax

logger = logging.getLogger(__name__)


class Max(QMax):
    def add_client(self, client, offset_to_current=0, client_position=None):
        if client in self.clients:
            return
        return self.clients.add_client(
            client, offset_to_current, client_position
        )

    def focus_previous(self, window):
        client = self.clients.focus_previous(window)
        return self.clients[-1] if not client else client

    def focus_next(self, window):
        client = self.clients.focus_next(window)
        return self.clients[0] if not client else client
