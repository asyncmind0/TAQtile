import logging
from libqtile.layout.max import Max as QMax
from libqtile.command.base import expose_command
from taqtile.log import logger

# logger = logging.getLogger(__name__)


class Max(QMax):
    @expose_command("previous")
    def up(self):
        if self.clients.current_client is None:
            client = self.clients[0]
            logger.error(f"up: current client {client}")
        else:
            idx = self.clients.index(self.clients.current_client) - 1
            if idx < 0:
                idx = len(self.clients.clients) - 1
            client = self.clients.clients[idx]
            logger.error(
                f"up: current client {client}  {self.clients.index(client)+1}/{len(self.clients)}"
            )
        self.group.focus(client, True)

    @expose_command("next")
    def down(self):
        if self.clients.current_client is None:
            client = self.clients[0]
            logger.error(f"down: current client {client}")
        else:
            idx = self.clients.index(self.clients.current_client) + 1
            if idx == len(self.clients.clients):
                idx = 0

            client = self.clients.clients[idx]
            logger.error(
                f"down: current client {client}  {self.clients.index(client)+1}/{len(self.clients)}"
            )
        self.group.focus(client, True)
