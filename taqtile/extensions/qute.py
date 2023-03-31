from libqtile.hook import subscribe
from taqtile.extensions.base import WindowGroupList
from taqtile.system import (
    get_current_window,
    get_hostconfig,
)
from libqtile import qtile
import logging

logger = logging.getLogger("taqtile")


@subscribe.client_name_updated
def trigger_dgroups(client):
    profiles = set(
        [
            x["profile"].lower()
            for x in get_hostconfig("browser_accounts", {}).values()
        ]
    )
    if "WhatsApp - web.whatsapp.com" in client.name:
        client.togroup("webcon")
        return
    for profile in profiles:
        if qtile.groups_map.get(profile) and profile in str(client.name):
            client.togroup(profile)
