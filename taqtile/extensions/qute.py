from libqtile.hook import subscribe
from taqtile.extensions.base import WindowGroupList
from taqtile.system import (
    get_current_window,
    get_hostconfig,
)
from libqtile import qtile


@subscribe.client_name_updated
def trigger_dgroups(client):
    profiles = [
        x["profile"] for x in get_hostconfig("browser_accounts", {}).values()
    ]
    for profile in profiles:
        if qtile.groups_map.get("profile") and profile in client.name:
            client.togroup(profile)


class Qute(WindowGroupList):
    """
    Give vertical list of all open qutebrowser windows in dmenu. Switch to selected.
    """

    dmenu_prompt = "Qute"

    def match_item(self, win):
        # logger.info(dir(win.window))
        if win.window.get_wm_class()[0] != "qutebrowser":
            return
        return self.item_format.format(
            group=win.group.label or win.group.name,
            id=id,
            window=win.name.split("|", 1)[-1],
        )

    def spawn(self, sout):
        if sout.startswith("http"):
            self.qtile.spawn(
                # "/usr/sbin//systemd-run --user --slice=browser.slice /usr/local/bin/surf %s"
                "surf %s"
                % sout.strip()
            )
        elif sout:
            gg = "gg "
            if sout.startswith(gg):
                sout = sout.split(gg)[-1]
                cmd = "qutebr https://www.google.com/search?q='%s'&ie=utf-8&oe=utf-8"
            else:
                cmd = "surf https://duckduckgo.com/?t=ffab&q=%s&ia=web"
            self.qtile.spawn(cmd % quote_plus(sout))
