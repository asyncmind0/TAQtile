import os
from os.path import expanduser, isdir, join, pathsep
from plumbum.cmd import dmenu, emacsclient
from recent_runner import RecentRunner
import threading

from log import logger

def dmenu_show(title, items):
    from themes import dmenu_defaults
    import shlex
    dmenu_defaults = shlex.split(dmenu_defaults)
    logger.info("DMENU: %s", dmenu_defaults)
    try:
        return (dmenu[
            "-i", "-p", "[%s] >>> " % title
            ] << "\n".join(items))(*dmenu_defaults).strip()
    except Exception as e:
        logger.exception("error running dmenu")


def list_windows(qtile, current_group=False):

    def title_format(x):
        return "[%s] %s" % (
            x.group.name if x.group else '',
            x.name)

    if current_group:
        window_titles = [
            w.name for w in qtile.groupMap[qtile.currentGroup.name].windows
            if w.name != "<no name>"
        ]
    else:
        window_titles = [
            title_format(w) for w in qtile.windowMap.values() if w.name != "<no name>"
        ]
    logger.info(window_titles)

    def process_selected(selected):
        if not current_group:
            group, selected = selected.split(']', 1)
        selected = selected.strip()
        logger.info("Switch to: %s", selected)
        for window in qtile.windowMap.values():
            try:
                if window.group and str(window.name) == str(selected):
                    logger.debug("raise %s:", window)
                    if window.group.screen:
                        qtile.cmd_to_screen(window.group.screen.index)
                    else:
                        window.group.cmd_toscreen()
                    qtile.currentGroup.focus(window, False)
                    return True
            except Exception as e:
                logger.exception("error in group")
        return True

    process_selected(dmenu_show(
        qtile.currentGroup.name if current_group else "*",
        window_titles,
    ))


def list_windows_group(qtile):
    return list_windows(qtile, current_group=True)


def list_executables():
    paths = os.environ["PATH"].split(pathsep)
    executables = []
    for path in filter(isdir, paths):
        for file_ in os.listdir(path):
            if os.access(join(path, file_), os.X_OK):
                executables.append(file_)
    return set(executables)


def dmenu_run(qtile):
    recent = RecentRunner('qtile_run')
    selected = dmenu_show("Run", recent.list(list_executables()))
    print(selected)
    if not selected:
        return
    logger.debug((dir(qtile)))
    qtile.cmd_spawn(selected)
    recent.insert(selected)


def dmenu_org(qtile):
    org_categories = [
        "todo",
        "event",
        "note",
    ]
    title = dmenu_show("Run", org_categories)
    cmd_str = (
        "emacsclient -f xdev -c org-protocol://capture://"
        "url/%s/etext" % (
            title,
        )
    )
    qtile.cmd_spawn(cmd_str)
