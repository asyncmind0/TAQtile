from __future__ import print_function
import logging
import os
from libqtile import hook, window
from system import get_hostconfig, get_num_monitors, execute_once


num_monitors = get_num_monitors()

event_cntr = 2
prev_timestamp = 0
initial_num_mons = get_num_monitors()
all_desktops = ['tail']

log = logging.getLogger("qtile")

log.error("INITIALIZING  hooks")


#@hook.subscribe.setgroup
def move_special_windows():
    for name in all_desktops:
        for w in hook.qtile.windowMap.values():
            if w.group and (
                    w.match(wname=name)
                    or (hasattr(window, 'name') and window.name == name)):
                w.cmd_togroup(hook.qtile.currentGroup.name)


@hook.subscribe.screen_change
def restart_on_randr(qtile, ev):
    print("Screen change: %s", ev.__dict__)
    global event_cntr, prev_timestamp
    cur_timestamp = ev.timestamp
    # num_mons = get_num_monitors()
    if abs(prev_timestamp - cur_timestamp) > 1000:
        # and num_mons != initial_num_mons:
        # if num_screens != get_num_monitors():
        # signal.signal(signal.SIGCHLD, signal.SIG_DFL)
        print("RESTART screen change")
        qtile.cmd_restart()
    else:
        prev_timestamp = cur_timestamp


@hook.subscribe.startup
def startup():
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


def should_be_floating(w):
    for floating in float_windows:
        if w.match(wname=floating, wmclass=floating, role=floating):
            return True
    return w.window.get_wm_type() == 'dialog' or bool(
        w.window.get_wm_transient_for())


@hook.subscribe.startup
@hook.subscribe.window_name_change
def set_groups():
    for client in hook.qtile.windowMap.values():
        for rule in hook.qtile.dgroups.rules:
            log.error('Group rule %s' %  rule)
            if rule.matches(client):
                if rule.group:
                    try:
                        client.togroup(rule.group)
                    except Exception as e:
                        log.exception("Ignored exception switching group")


@hook.subscribe.startup
def dbus_register():
    import subprocess
    x = os.environ.get('DESKTOP_AUTOSTART_ID')
    if not x:
        return
    subprocess.Popen(['dbus-send',
                      '--session',
                      '--print-reply=string',
                      '--dest=org.gnome.SessionManager',
                      '/org/gnome/SessionManager',
                      'org.gnome.SessionManager.RegisterClient',
                      'string:qtile',
                      'string:' + x])


@hook.subscribe.window_name_change
def apply_rules(*args, **kwarg):
    windows = [
        i for i in hook.qtile.windowMap.values()
        if not isinstance(i, window.Internal)]
    for client in windows:
        try:
            window_class = client.window.get_wm_class()
            window_class, instance_class = window_class if window_class else ('', '')
            window_type = client.get_wm_type() if hasattr(
                client, 'get_wm_type') else ''
            window_name = client.name
            if window_class in ["screenkey", "kruler", 'Dunst']:
                client.static(0)
            #if window_class == "screenkey" and window_type != 'dialog':
            #    client.place(100, 100, 800, 50, 2, 2, '00C000')
            if window_name in ["shrapnel", "*Org Select*", 'ncmpcpp']:
                if hasattr(client, 'applied'):
                    continue
                client.applied = True
            if window_class.startswith('crx_'):
                client.applied = True
                try:
                    client.togroup('comm2')
                except Exception:
                    log.exception("client_new hook")
        except Exception as e:
            log.exception("client_new hook")


#@hook.subscribe.client_new
def client_new(client, *args, **kwargs):
    log.error("client_new:%s" % client.window.get_name())
    if client.window.get_name() == 'shrapnel':
        client.cmd_enable_floating()
        client.place(500, 50, 800, 400, 1, None, above=True, force=True)#, '00C000')
        client.cmd_opacity(0.85)
        # client.static(0)


#@hook.subscribe.client_managed
#def move_windows_multimonitor(window):
#    screen_preferences = get_hostconfig('screen_affinity')
#    for name, screen in screen_preferences.items():
#        if hasattr(window, 'match') and window.match(title=name):
#            log.debug(window.group)
#            try:
#                win_group = int(window.group.name)
#                # TODO handle cases for more than 2 monitors
#                if win_group < 10 and num_monitors > 1 and screenno > 1:
#                    window.togroup(str(win_group + 10))
#            except ValueError as e:
#                log.debug("not an integer group")
#    # if should_be_floating(window.window):
#    #    window.window.floating = True
