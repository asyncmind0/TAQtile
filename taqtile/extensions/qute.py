from libqtile.hook import subscribe
from datetime import datetime, timedelta
import re
from taqtile.extensions.base import WindowGroupList
from taqtile.system import (
    get_current_window,
    get_hostconfig,
)
from libqtile import qtile
import threading
import logging


logger = logging.getLogger("taqtile")


@subscribe.client_name_updated
def trigger_dgroups(client):
    accounts = get_hostconfig("browser_accounts", {})
    if not client.name:
        return
    if "WhatsApp - web.whatsapp.com" in client.name:
        client.togroup("webcon")
        return
    for user, config in accounts.items():
        for app in ["calendar", "mail"]:
            app_regex = config.get(app, {}).get("regex")
            if re.match(app_regex, client.name, re.I):
                client.togroup(app)
                return
        profile = config.get("profile", "").lower()
        if qtile.groups_map.get(profile) and profile in str(client.name):
            client.togroup(profile)
