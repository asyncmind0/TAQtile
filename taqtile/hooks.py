import signal
import logging
import os
from random import randint
from subprocess import check_output

from libqtile import hook
from libqtile.utils import send_notification
from taqtile.system import (
    get_hostconfig,
    get_num_monitors,
    execute_once,
    hdmi_connected,
    get_windows_map,
)


logger = logging.getLogger(__name__)


num_monitors = get_num_monitors()
prev_timestamp = 0
prev_state = hdmi_connected()


# @hook.subscribe.screen_change
def restart_on_randr(qtile, ev):
    logger.error("Screen change: %s", ev.__dict__)
    return
    global event_cntr, prev_timestamp
    cur_timestamp = ev.timestamp
    num_mons = get_num_monitors()
    # if len(qtile.screens) != num_mons:
    if num_mons == 2:
        check_output(["dualmonitor"])
    elif num_mons == 1:
        check_output(["singlemonitor"])
    qtile.restart()


def dialogs(window):
    if (
        window.window.get_wm_type() == "dialog"
        or window.window.get_wm_transient_for()
    ):
        window.floating = True


@hook.subscribe.startup
def startup():
    # http://stackoverflow.com/questions/6442428/how-to-use-popen-to-run-backgroud-process-and-avoid-zombie
    # signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    commands = get_hostconfig("autostart-once") or {}
    num_mons = get_num_monitors()
    logger.debug("Num MONS:%s", num_mons)
    # for command, kwargs in commands.items():
    #    logger.debug("executing command %s", kwargs)
    #    try:
    #        execute_once(command, **(kwargs if kwargs else {}))
    #    except Exception as e:
    #        logger.exception("error in startup hook")
    #        # send_notification("Qtile startup apps errored.", "")
    from libqtile import qtile

    qtile.togroup("home")


@hook.subscribe.shutdown
def shutdown():
    pass


# @hook.subscribe.startup
def dbus_register():
    try:
        import subprocess

        x = os.environ.get("DESKTOP_AUTOSTART_ID")
        if not x:
            return
        subprocess.Popen(
            [
                "dbus-send",
                "--session",
                "--print-reply=string",
                "--dest=org.gnome.SessionManager",
                "/org/gnome/SessionManager",
                "org.gnome.SessionManager.RegisterClient",
                "string:qtile",
                "string:" + x,
            ]
        )
    except Exception as e:
        logger.exception("error in dbus_register")


@hook.subscribe.client_managed
def rules_shrapnel(client):
    client_name = client.window.get_name()
    if client_name == "shrapnel":
        client.enable_floating()
        client.place(
            randint(500, 550),
            randint(50, 100),
            800,
            400,
            1,
            None,
            above=True,
        )
        client.set_opacity(0.85)


@hook.subscribe.client_name_updated
def trigger_dgroups(client):
    try:
        if client.name and "brave" in client.name.lower():
            pid = client.window.get_net_wm_pid()
            client.window.set_property(
                "QTILE_PROFILE",
                "TEST",
                type="UTF8_STRING",
                format=8,
            )
            from libqtile import qtile

            qtile.dgroups._add(client)
    except:
        logger.exception("Error in trigger_dgroups")


# @hook.subscribe.current_screen_change
# def screen_change():
#    from libqtile import qtile
#
#    for client in qtile.windows_map.values():
#        for rule in qtile.dgroups.rules:
#            try:
#                if rule and rule.matches(client):
#                    if getattr(rule, "sticky", False) or getattr(
#                        client, "sticky", False
#                    ):
#                        logger.info(
#                            f" setting sticky {client}:{qtile.current_group}"
#                        )
#                        client.togroup(qtile.current_group)
#            except Exception as e:
#                logger.error("error setting sticky %s", client)


@hook.subscribe.client_managed
def set_group(client):
    from libqtile import qtile

    for rule in qtile.dgroups.rules:
        try:
            if client.__class__.__name__ in [
                "Icon",
                "Internal",
                "Systray",
            ]:
                continue
            if rule and rule.matches(client):
                logger.info(f"Matched {rule} {client}")
                if rule.group:
                    logger.error("to group %s", rule.group)
                    client.togroup(rule.group)
                front = getattr(rule, "front", False)
                if front and hasattr(client, "cmd_bring_to_front"):
                    logger.error("to front %s", client.window.get_name())
                    client.bring_to_front()
                client.floating = rule.float
                if getattr(rule, "fullscreen", None):
                    if rule.fullscreen:
                        client.fullscreen = True
                    else:
                        client.fullscreen = False
                if getattr(rule, "static", False):
                    client.static(0)
                if getattr(rule, "opacity", False):
                    client.set_opacity(rule.opacity)
                center = getattr(rule, "center", False)
                if center:
                    logger.debug(dir(qtile.current_screen))
                    client.tweak_float(
                        x=(qtile.current_screen.width / 2) - (client.width / 2),
                        y=(qtile.current_screen.height / 2)
                        - (client.height / 2),
                    )
                # current_screen = getattr(rule, 'current_screen', False)
                # if current_screen:
                #    client.to_group(hook.get_current_screen(qtile).group)
                geometry = getattr(rule, "geometry", False)
                if geometry:
                    client.place(
                        geometry["x"],
                        geometry["y"],
                        geometry["width"],
                        geometry["height"],
                        1,
                        None,
                        above=True,
                        # force=True,
                    )  # , '00C000')

                if rule.break_on_match:
                    break
        except Exception as e:
            logger.exception("error setting rules %s", client)


def set_groups(qtile):
    from libqtile import qtile

    for client in list(get_windows_map(qtile).values()):
        logger.debug(f"set_groups {client}")
        set_group(client)


# @hook.subscribe.client_urgent_hint_changed
# def urgent_hint_changed(*args, **kwargs):
#    logger.debug("urgent_hint_changed called with %s %s", args, kwargs)


# @hook.subscribe.selection_change
# def selection_change(source, selection=None):
#    #logger.debug("selection_change called with %s %s", source, selection)
#    if source == 'CLIPBOARD' and selection['selection']:
#        recent = RecentRunner('qtile_clip', '~/.qtile_clip.db')
#        recent.insert(selection['selection'])
#    logger.debug("selection_change inserted %s %s",  selection, source)

# @hook.subscribe.selection_notify
# def selection_notify(*args, **kwargs):
#    logger.debug("selection_notify called with %s %s", args, kwargs)
