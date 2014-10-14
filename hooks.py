import logging
import os
import signal

from libqtile import hook, window

from system import get_hostconfig, get_num_monitors, execute_once


num_monitors = get_num_monitors()

event_cntr = 2
prev_timestamp = 0
initial_num_mons = get_num_monitors()
all_desktops = ['tail']

log = logging.getLogger("qtile")

log.error("importin hooks")


@hook.subscribe.setgroup
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
    num_mons = get_num_monitors()
    if abs(prev_timestamp - cur_timestamp) > 1000:
        # and num_mons != initial_num_mons:
        # if num_screens != get_num_monitors():
        #signal.signal(signal.SIGCHLD, signal.SIG_DFL)
        print("RESTART screen change")
        qtile.cmd_restart()
    else:
        prev_timestamp = cur_timestamp


@hook.subscribe.startup
def startup():
    # http://stackoverflow.com/questions/6442428/how-to-use-popen-to-run-backgroud-process-and-avoid-zombie
    #signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    commands = get_hostconfig('autostart-once')
    num_mons = get_num_monitors()
    log.debug("Num MONS:%s", num_mons)
    # log.debug("Num DeSKTOPS:%s", len(qtile.screens))
    if num_mons > 1:
        commands[os.path.expanduser("dualmonitor")] = None
    elif num_mons == 1:
        commands[os.path.expanduser("rightmonitor")] = None

    for command, process_filter in commands.iteritems():
        execute_once(command, process_filter, hook.qtile)


def should_be_floating(w):
    for floating in float_windows:
        if w.match(wname=floating, wmclass=floating, role=floating):
            return True
    return w.window.get_wm_type() == 'dialog' or bool(
        w.window.get_wm_transient_for())


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


@hook.subscribe.client_new
def new_client(client):
    try:
        window_class = client.window.get_wm_class()[0]
        window_type = client.get_wm_type() if hasattr(
            client, 'get_wm_type') else ''
        window_name = client.window.get_name()
        if window_class in [
                "screenkey", "kruler"]:
            client.static(0)
        if window_class == "screenkey" and window_type != 'dialog':
            client.place(100, 100, 800, 50, 2, 2, '00C000')
        if window_name == "st":
            client.window.floating = 1
            client.place(50, 30, 500, 400, 1, None, force=True)#, '00C000')
        log.debug(window_class)
        log.debug(window_type)
    except Exception as e:
        log.exception("client_new hook")


@hook.subscribe.client_managed
def move_windows_multimonitor(window):
    screen_preferences = get_hostconfig('screen_preferences')
    for screenno, pref in screen_preferences.iteritems():
        for rule in pref:
            if hasattr(window, 'match') and window.match(**rule):
                log.debug(window.group)
                try:
                    win_group = int(window.group.name)
                    # TODO handle cases for more than 2 monitors
                    if win_group < 10 and num_monitors > 1 and screenno > 1:
                        window.togroup(str(win_group + 10))
                except ValueError as e:
                    log.debug("not an integer group")
    # if should_be_floating(window.window):
    #    window.window.floating = True


@hook.subscribe.window_name_change
def change_name():
    try:
        windows = [
            i for i in hook.qtile.windowMap.values()
            if not isinstance(i, window.Internal)]
        for win in windows:
            if hasattr(win, 'defunct'):
                hook.qtile.dgroups._add(win)
    except Exception as e:
        log.exception("change_name")
