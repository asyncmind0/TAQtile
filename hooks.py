from libqtile.config import Key, Click, Drag, Screen, Group, Match, Rule
from libqtile.command import lazy, CommandObject
from libqtile import layout, bar, widget, hook

from system import get_hostconfig, get_num_monitors, execute_once
from screens import get_screens, PRIMARY_SCREEN, SECONDARY_SCREEN
from keys import get_keys
from config import float_windows, num_monitors
import logging
import os
import re

log = logging.getLogger("qtile.screen")
event_cntr = 2
prev_timestamp = 0

@hook.subscribe.screen_change
def restart_on_randr(qtile, ev):
    log.debug(ev.__dict__)
    global event_cntr, prev_timestamp
    cur_timestamp = ev.timestamp
    if abs(prev_timestamp - cur_timestamp) > 1000:
        #if num_screens != get_num_monitors():
        import signal
        signal.signal(signal.SIGCHLD, signal.SIG_DFL)
        log.debug("RESTART screen change")
        qtile.cmd_restart()
    else:
        prev_timestamp = cur_timestamp


@hook.subscribe.startup
def startup():
    # http://stackoverflow.com/questions/6442428/how-to-use-popen-to-run-backgroud-process-and-avoid-zombie
    import signal
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    commands = get_hostconfig('autostart-once')
    num_mons = get_num_monitors()
    log.debug("Num MONS:%s", num_mons)
    #log.debug("Num DeSKTOPS:%s", len(qtile.screens))
    if num_mons > 1:
        commands[os.path.expanduser("dualmonitor")] = None
    elif num_mons == 1:
        commands[os.path.expanduser("rightmonitor")] = None

    for command, process_filter in commands.iteritems():
        execute_once(command, process_filter)


def should_be_floating(w):
    wm_class = w.get_wm_class()
    wm_role = w.get_wm_window_role()
    if wm_role in ['buddy_list']:
        return False
    if not wm_class:
        return False
    if isinstance(wm_class, tuple):
        for cls in wm_class:
            if cls.lower() in float_windows:
                return True
    else:
        if wm_class.lower() in float_windows:
            return True
    return w.get_wm_type() == 'dialog' or bool(w.get_wm_transient_for())


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
    if client.window.get_wm_class()[0] in [
            "screenkey", "kruler"]:
        client.static(0)


@hook.subscribe.client_managed
def move_windows_multimonitor(window):
    screen_preferences = get_hostconfig('screen_preferences')
    for screenno, pref in screen_preferences.iteritems():
        for rule in pref:
            if window.match(**rule):
                log.debug(window.group)
                win_group = int(window.group.name)
                # TODO handle cases for more than 2 monitors
                if win_group < 10 and num_monitors > 1 and screenno > 1:
                    window.togroup(str(win_group+10))


@hook.subscribe.client_managed
def dialogs(window):
    window_rules = [
        {
            'wmclass': "Google-chrome-stable",
            'wmrole': "pop-up",
            'wmname': r"^Developer.*",
            'wm_icon_name': r"^Developer.*",
            'action': ['togroup', '16'],
            'exclusive': True
        },
        {
            'wmclass': "google-chrome-stable",
            'wmrole': "pop-up",
            'wmname': r"^(?!Developer).*",
            'action': [],
            'exclusive': True
        },
        {
            'wmclass': "Google-chrome-stable",
            'wmrole': "pop-up",
            'wmname': r"^(?!Developer).*",
            'action': ['togroup', '6'],
            'exclusive': False
        },
    ]
    try:
        for rule in window_rules:
            #log.debug("'%s':'%s'", rule['wmname'], window.cmd_inspect())
            if rule['wmclass'] in window.window.get_wm_class() \
               and rule['wmrole'] == window.window.get_wm_window_role()\
               and re.match(rule['wmname'], window.name):
                if 'wm_icon_name' in rule:
                    if not re.match(rule['wm_icon_name'],
                                    window.get_wm_icon_name()):
                        continue
                action = rule['action']
                try:
                    getattr(window, action.pop(0))(*action)
                except Exception as e:
                    log.exception("Action failed, %s", rule)
                if rule.get('exclusive', False):
                    #log.debug("%s matched exclusive %s", window.name, rule)
                    break
    except:
        log.exception("Error rule matching.")

    if should_be_floating(window.window):
        window.floating = True
