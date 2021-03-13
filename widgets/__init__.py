import logging
import subprocess
import threading

from libqtile.widget import NetGraph, Clock

from extra import RaiseWindowOrSpawn
from pytz import timezone
from datetime import datetime
from system import execute_once


from log import logger


# class ThreadedPacman(widget.Pacman):
#
#    def __init__(self, *args, **kwargs):
#        super(ThreadedPacman, self).__init__(*args, **kwargs)
#        self.timeout_add(self.update_interval, self.wx_updater)
#        self.wx_updater()
#
#    def update(self, data=None):
#        if self.configured and data:
#            self.updates_data = str(data)
#            if self.text != self.updates_data:
#                self.text = self.updates_data
#                self.bar.draw()
#        return "N/A"
#
#    def wx_updater(self):
#        logger.warn('adding WX Pacman widget timer')
#        import gobject
#
#        def worker():
#            pacman = subprocess.Popen(['checkupdates'], stdout=subprocess.PIPE)
#            data = len(pacman.stdout.readlines())
#            gobject.idle_add(self.update, data)
#        threading.Thread(target=worker).start()
#        return True


class Clock(Clock):
    def poll(self):
        # We use None as a sentinel here because C's strftime defaults to UTC
        # if TZ=''.
        if self.timezone is not None:
            zoneinfo = timezone("UTC")
            return (
                zoneinfo.localize(datetime.utcnow() + self.DELTA)
                .astimezone(self.timezone)
                .strftime(self.format)
            )
        else:
            return self._get_time()


class CalClock(Clock):
    # def button_release(self, x, y, button):

    def button_press(self, x, y, button):
        # self.qtile.cmd_spawn("calendar_applet.py")
        try:
            self.qtile.current_screen.bottom.show(
                not self.qtile.current_screen.bottom.is_show()
            )
        except:
            logger.exception("error")
        execute_once("kworldclock", qtile=self.qtile, toggle=True)
        # rws = RaiseWindowOrSpawn(wmname="TDE World Clock", cmd="/opt/trinity/bin/kworldclock")
        # rws(self.qtile)


# class GraphHistory(NetGraph):
#    """Graph that persists history and reloads it when restarted.
#    provides a continuous graph, desipite qtile restarting.
#    """
#    default_store = None
#
#    def push(self, value):
#        return super().push(value)
