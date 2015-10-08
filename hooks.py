from __future__ import print_function
import logging
import os
from libqtile import hook, window
from system import get_hostconfig, get_num_monitors, execute_once


num_monitors = get_num_monitors()
prev_timestamp = 0
log = logging.getLogger(__name__)
log.error("INITIALIZING  hooks")


@hook.subscribe.screen_change
def restart_on_randr(qtile, ev):
    print("Screen change: %s", ev.__dict__)
    global event_cntr, prev_timestamp
    cur_timestamp = ev.timestamp
    # num_mons = get_num_monitors()
    if abs(prev_timestamp - cur_timestamp) > 1000:
        # if num_screens != get_num_monitors():
        # signal.signal(signal.SIGCHLD, signal.SIG_DFL)
        print("RESTART screen change")
        qtile.cmd_restart()
    else:
        prev_timestamp = cur_timestamp


@hook.subscribe.startup
def startup():
    try:
        # http://stackoverflow.com/questions/6442428/how-to-use-popen-to-run-backgroud-process-and-avoid-zombie
        # signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        commands = get_hostconfig('autostart-once')
        num_mons = get_num_monitors()
        log.debug("Num MONS:%s", num_mons)
        # log.debug("Num DeSKTOPS:%s", len(qtile.screens))
        if num_mons > 1:
            commands[os.path.expanduser("dualmonitor")] = None
        elif num_mons == 1:
            commands[os.path.expanduser("rightmonitor")] = None

        for command, process_filter in commands.items():
            execute_once(command, process_filter, hook.qtile)
    except Exception as e:
        log.exception("error in startup hook")


@hook.subscribe.startup
def dbus_register():
    try:
        import subprocess
        x = os.environ.get('DESKTOP_AUTOSTART_ID')
        if not x:
            return
        subprocess.Popen([
            'dbus-send',
            '--session',
            '--print-reply=string',
            '--dest=org.gnome.SessionManager',
            '/org/gnome/SessionManager',
            'org.gnome.SessionManager.RegisterClient',
            'string:qtile',
            'string:' + x])
    except Exception as e:
        log.exception("error in dbus_register")


@hook.subscribe.client_new
def client_new(client, *args, **kwargs):
    log.error("client_new:%s" % client.window.get_name())
    log.error("client_new:%s, %s" % client.window.get_wm_class())
    if client.window.get_name() == 'shrapnel':
        client.cmd_enable_floating()
        client.place(
            500, 50, 800, 400, 1, None, above=True, force=True)#, '00C000')
        client.cmd_opacity(0.85)


@hook.subscribe.setgroup
def set_groups(*args, **kwargs):
    for client in hook.qtile.windowMap.values():
        for rule in hook.qtile.dgroups.rules:
            if rule.matches(client):
                if rule.group:
                    try:
                        client.togroup(rule.group)
                    except Exception as e:
                        logging.exception("error setting groups")
    for w in hook.qtile.windowMap.values():
        log.info(w)
        cliclass = w.window.get_wm_class()
        if cliclass and cliclass[1] == 'Conkeror':
            w.cmd_disable_floating()
            w.cmd_disable_fullscreen()
