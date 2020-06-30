from libqtile.extension import Dmenu, WindowList, DmenuRun
from log import logger
import os
from recent_runner import RecentRunner
from dmenu import list_executables
from subprocess import Popen


class Surf(Dmenu):
    """
    Give vertical list of all open windows in dmenu. Switch to selected.
    """

    defaults = [
        ("item_format", "* {window}", "the format for the menu items"),
        ("all_groups", True, "If True, list windows from all groups; otherwise only from the current group"),
        ("dmenu_lines", "80", "Give lines vertically. Set to None get inline"),
    ]

    def __init__(self, **config):
        Dmenu.__init__(self, **config)
        self.add_defaults(WindowList.defaults)

    def _configure(self, qtile):
        Dmenu._configure(self, qtile)
        self.dbname = 'qtile_surf'

    def list_windows(self):
        id = 0
        self.item_to_win = {}

        if self.all_groups:
            windows = self.qtile.windows_map.values()
        else:
            windows = self.qtile.current_group.windows

        for win in windows:
            if win.group:
                #logger.info(dir(win.window))
                if win.window.get_wm_class()[0] != 'surf':
                    continue
                item = self.item_format.format(
                    group=win.group.label
                    or win.group.name,
                    id=id,
                    window=win.name
                )
                self.item_to_win[item] = win
                id += 1

    def run(self):
        self.list_windows()
        #logger.info(self.item_to_win)
        recent = RecentRunner(self.dbname)
        out = super().run(
            items=(
                [x for x in self.item_to_win.keys()] +
                [x for x in recent.list([])]
            )
        )
        screen = self.qtile.current_screen

        try:
            sout = out.rstrip('\n')
        except AttributeError:
            # out is not a string (for example it's a Popen object returned
            # by super(WindowList, self).run() when there are no menu items to
            # list
            screen.set_group("surf")
            return

        recent.insert(
            sout[2:]
            if sout.startswith('*')
            else sout
        )
        try:
            win = self.item_to_win[sout]
        except KeyError:
            # The selected window got closed while the menu was open?
            if sout.startswith('http'):
                self.qtile.cmd_spawn("surf %s" % sout.strip())
            elif sout:
                self.qtile.cmd_spawn("surf https://www.google.com/search?q='%s'&ie=utf-8&oe=utf-8" % sout)
            return

        screen.set_group(win.group)
        win.group.focus(win)
        logger.info(
            win.window.get_property(
                '_SURF_URI',
                'STRING'
            ).value.to_string()
        )


class DmenuRunRecent(DmenuRun):
    defaults = [
        ("dbname", 'dbname', "the sqlite db to store history."),
        ("dmenu_command", 'dmenu', "the dmenu command to be launched"),
    ]
    def __init__(self, **config):
        super(DmenuRunRecent, self).__init__(**config)
        self.add_defaults(super(DmenuRunRecent, self).defaults)

    def _configure(self, qtile):
        self.qtile = qtile
        self.dbname = 'qtile_run'
        self.dmenu_command = 'dmenu'
        super(DmenuRunRecent, self)._configure(qtile)

    def run(self):
        logger.error("running")
        recent = RecentRunner(self.dbname)
        selected = super(DmenuRunRecent, self).run(
            items=[x for x in recent.list(
                list_executables())]).strip()
        logger.info(selected)
        if not selected:
            return
        recent.insert(selected)
        return Popen(
            ["nohup", selected],
            stdout=None,
            stdin=None,
            preexec_fn=os.setpgrp
        )
        #system("%s & disown " % selected)
        #lazy.cmd_spawn(selected)
        #self.qtile.cmd_spawn(selected)
        return selected
