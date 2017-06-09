import logging
import subprocess
import threading

from libqtile import widget


from log import logger


class ThreadedPacman(widget.Pacman):

    def __init__(self, *args, **kwargs):
        super(ThreadedPacman, self).__init__(*args, **kwargs)
        self.timeout_add(self.update_interval, self.wx_updater)
        self.wx_updater()

    def update(self, data=None):
        if self.configured and data:
            self.updates_data = str(data)
            if self.text != self.updates_data:
                self.text = self.updates_data
                self.bar.draw()
        return "N/A"

    def wx_updater(self):
        logger.warn('adding WX Pacman widget timer')
        import gobject

        def worker():
            pacman = subprocess.Popen(['checkupdates'], stdout=subprocess.PIPE)
            data = len(pacman.stdout.readlines())
            gobject.idle_add(self.update, data)
        threading.Thread(target=worker).start()
        return True


class CalClock(widget.Clock):
    # def button_release(self, x, y, button):

    def button_press(self, x, y, button):
        self.qtile.cmd_spawn("calendar_applet.py")


class GraphHistory(widget.NetGraph):
    """Graph that persists history and reloads it when restarted.
    provides a continuous graph, desipite qtile restarting.
    """
    default_store = None

    def __init__(self, *args, **kwargs):
        super(widget.NetGraph, self).__init__(*args, **kwargs)

    def push(self, value):
        return super(widget.NetGraph, self).push(value)
