from __future__ import print_function
import os
from random import randint
from libqtile import hook
from libqtile.layout import Slice
from system import get_hostconfig, get_num_monitors, execute_once, hdmi_connected, get_windows_map
from recent_runner import RecentRunner
from os.path import splitext, basename
from subprocess import check_output

from log import logger

num_monitors = get_num_monitors()
prev_timestamp = 0
prev_state = hdmi_connected()


@hook.subscribe.screen_change
def restart_on_randr(qtile, ev):
    logger.debug("Screen change: %s", ev.__dict__)
    global event_cntr, prev_timestamp
    cur_timestamp = ev.timestamp
    num_mons = get_num_monitors()
    if len(qtile.screens) != num_mons:
        if num_mons == 2:
            check_output(["dualmonitor"])
        if num_mons == 1:
            check_output(["singlemonitor"])
        qtile.cmd_restart()
    if hdmi_connected() == prev_state:
        return
    if abs(prev_timestamp - cur_timestamp) > 1000:
        # if num_screens != get_num_monitors():
        # signal.signal(signal.SIGCHLD, signal.SIG_DFL)
        print("RESTART screen change")
        qtile.cmd_restart()
    else:
        prev_timestamp = cur_timestamp


def load_sounds():
    for sound in [
                "/usr/share/sounds/freedesktop/stereo/audio-volume-change.oga"
                ]:
        check_output([
            "pactl",
            "upload-sample",
            sound,
            splitext(basename(sound))[0]
                      ]
        )

@hook.subscribe.startup
def startup():
    try:
        # http://stackoverflow.com/questions/6442428/how-to-use-popen-to-run-backgroud-process-and-avoid-zombie
        # signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        commands = get_hostconfig('autostart-once') or {}
        num_mons = get_num_monitors()
        logger.debug("Num MONS:%s", num_mons)
        # logger.debug("Num DeSKTOPS:%s", len(qtile.screens))
        if num_mons > 1:
            commands[get_hostconfig('dual_monitor')] = None
        elif num_mons == 1:
            commands[get_hostconfig('single_monitor')] = None

        for command, kwargs in commands.items():
            execute_once(command, qtile=hook.qtile, **(kwargs if kwargs else {}))
        load_sounds()
    except Exception as e:
        logger.exception("error in startup hook")


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
        logger.exception("error in dbus_register")


def rules_shrapnel(client):
    client_name = client.window.get_name()
    if client_name == 'shrapnel':
        client.cmd_enable_floating()
        client.place(
            randint(500, 550),
            randint(50, 100),
            800,
            400,
            1, None, above=True, force=True)#, '00C000')
        client.cmd_opacity(0.85)


@hook.subscribe.client_managed
def set_groups(*args, **kwargs):
    for client in list(get_windows_map(hook.qtile).values()):
        for rule in hook.qtile.dgroups.rules:
            if rule.matches(client):
                try:
                    client.floating = rule.float
                    if getattr(rule, 'fullscreen', None):
                        if rule.fullscreen:
                            client.enablemaximize()
                        else:
                            client.enablemaximize(state=4)
                    #if getattr(client, 'static', False):
                    #    client.static(0)
                    if getattr(rule, 'opacity', False):
                        client.cmd_opacity(rule.opacity)
                    if rule.group and getattr(client, 'togroup', None):
                        client.togroup(rule.group)
                    front = getattr(rule, 'front', False)
                    if front and hasattr(
                            client, 'cmd_bring_to_front'):
                        logger.error("to front %s", client.window.get_name())
                        client.cmd_bring_to_front()
                    center = getattr(rule, 'center', False)
                    if center:
                        logger.debug(dir(get_current_screen(hook.qtile)))
                        client.tweak_float(
                            x=(get_current_screen(hook.qtile).width/2) - (client.width/2),
                            y=(get_current_screen(hook.qtile).height/2) - (client.height/2)
                        )
                    #current_screen = getattr(rule, 'current_screen', False)
                    #if current_screen:
                    #    client.to_group(hook.get_current_screen(qtile).group)
                    geometry = getattr(rule, 'geometry', False)
                    if geometry:
                        client.place(
                            geometry['x'],
                            geometry['y'],
                            geometry['width'],
                            geometry['height'],
                            1, None, above=True, force=True)#, '00C000')
                        
                    if rule.break_on_match:
                        break
                except Exception as e:
                    logger.exception("error setting rules")


#@hook.subscribe.client_urgent_hint_changed
#def urgent_hint_changed(*args, **kwargs):
#    logger.debug("urgent_hint_changed called with %s %s", args, kwargs)


#@hook.subscribe.selection_change
#def selection_change(source, selection=None):
#    #logger.debug("selection_change called with %s %s", source, selection)
#    if source == 'CLIPBOARD' and selection['selection']:
#        recent = RecentRunner('qtile_clip', '~/.qtile_clip.db')
#        recent.insert(selection['selection'])
#    logger.debug("selection_change inserted %s %s",  selection, source)

#@hook.subscribe.selection_notify
#def selection_notify(*args, **kwargs):
#    logger.debug("selection_notify called with %s %s", args, kwargs)
