import os
import json

import re
import shlex
from os.path import isdir, join, pathsep, dirname

from plumbum.cmd import dmenu, pactl, recordmydesktop

from taqtile.log import logger
from taqtile.recent_runner import RecentRunner
from taqtile.screens import PRIMARY_SCREEN, SECONDARY_SCREEN
from taqtile.dbus_bluetooth import get_devices
from taqtile.themes import dmenu_cmd_args
from taqtile.system import (
    get_hostconfig,
    window_exists,
    get_windows_map,
    get_current_screen,
    get_current_group,
)
from taqtile.extra import terminal
from taqtile.log import logger


def dmenu_show(title, items):
    items = list(items)
    dmenu_args = shlex.split(dmenu_cmd_args(dmenu_lines=min(30, len(items))))
    logger.info("DMENU: %s", dmenu_args)
    try:
        return (dmenu["-c", "-i", "-p", "%s " % title] << "\n".join(items))(
            *dmenu_args
        ).strip()
    except Exception as e:
        logger.exception("error running dmenu")


def dmenu_org(qtile):
    org_categories = [
        "emacsclient",
        "todo",
        "event",
        "note",
    ]
    title = dmenu_show("Run", org_categories)
    if title == "emacsclient":
        cmd_str = "emacsclient -f xdev -c"
    else:
        cmd_str = (
            "emacsclient -f xdev -c org-protocol://capture://"
            "url/%s/etext" % (title,)
        )
    qtile.spawn(cmd_str)


def list_bluetooth(qtile):
    recent = RecentRunner("qtile_bluetooth")
    devices = get_devices()["/org/bluez/hci0"]["devices"]
    all_devices = {
        device["Alias"]: device["Address"] for device in devices.values()
    }
    selected = dmenu_show("Bluetooth:", recent.list(all_devices.keys()))
    if not selected:
        return
    action = dmenu_show("Action", ["connect", "disconnect", "music", "voice"])
    if action in ["music", "voice"]:
        from plumbum.cmd import pacmd

        logger.info(
            "bluez_card.%s",
            all_devices[selected].replace(":", "_"),
        )
        logger.info(
            pacmd(
                "set-card-profile",
                "bluez_card.%s" % all_devices[selected].replace(":", "_"),
                {"music": "a2dp_sink_aptx", "voice": "headset_head_unit"}[
                    action
                ],
            )
        )
    else:
        from plumbum.cmd import bluetoothctl

        (bluetoothctl << "%s %s\nexit\n" % (action, all_devices[selected]))()
    recent.insert(selected)


def get_window_titles(qtile):
    return [w["name"] for w in qtile.windows() if w["name"] != "<no name>"]


def dmenu_web(qtile):
    group = "monit"
    try:
        recent = RecentRunner("qtile_web")
        selected = dmenu_show("links:", recent.list([]))
        if not selected:
            return
        recent.insert(selected)
        if get_current_screen(qtile).index != SECONDARY_SCREEN:
            logger.debug("cmd_to_screen")
            qtile.to_screen(SECONDARY_SCREEN)
        if get_current_group(qtile).name != group:
            logger.debug("cmd_toggle_group")
            get_current_screen(qtile).toggle_group(group)
        window = window_exists(
            qtile, re.compile(r"mail.google.com__mail_u_%s" % selected, re.I)
        )
        if window:
            window = get_windows_map(qtile).get(window.window.wid)
            logger.debug("Matched" + str(window))
            window.togroup(group)
            logger.debug("layout.focus")
            get_current_group(qtile).focus(window)
        else:
            cmd = (
                'chromium --app="https://mail.google.com/mail/u/%s/#inbox"'
                % selected
            )

            logger.debug(cmd)
            qtile.spawn(cmd)
    except:
        logger.exception("error list_inboxes")


def dmenu_pushbullet(qtile):
    pushbullet_api_key = get_hostconfig("pushbullet_api_key", [])
    from pushbullet import PushBullet

    pb = PushBullet(pushbullet_api_key)
    device = dmenu_show("Devices:", [x.nickname for x in pb.devices])
    device = pb.get_device(device)
    title = "Select clip item to push: "
    dmenu_args = shlex.split(dmenu_cmd_args(dmenu_lines=min(30, len(items))))
    from plumbum.cmd import clipmenu

    body = clipmenu["-i", "-p", "%s" % title](*dmenu_args).strip()
    device.push_note("Shared from %s" % socket.gethostname(), open(body).read())


def dmenu_kubectl(qtile):
    from plumbum.cmd import kubectl

    clusters = kubectl("config", "get-clusters").split()[1:]
    cluster = dmenu_show("Cluster:", clusters)
    pods = json.loads(
        kubectl("--context", cluster, "get", "po", "-o", "json")
    ).get("items", [])
    containermap = {}
    for pod in pods:
        containermap[pod.get("metadata", {}).get("name", "unknown")] = [
            cont["name"] for cont in pod["spec"]["containers"]
        ]

    pod = dmenu_show("Pod:", containermap)

    op = dmenu_show("Operation", ["logs", "describe", "shell"])
    if op == "logs":
        container = dmenu_show("Container", containermap[pod])
        cmd = terminal(
            "k8s logs - %s - %s" % (pod, cluster),
            "kubectl --context=%s logs --tail=100 -f %s -c %s"
            % (cluster, pod, container),
        )
        logger.debug("k8s" + str(cmd))
        qtile.spawn(cmd)
    elif op == "describe":
        cmd = terminal(
            "k8s describe - %s - %s" % (pod, cluster),
            "kubectl --context=%s describe po %s;read" % (cluster, pod),
        )
        logger.debug("k8s" + str(cmd))
        qtile.spawn(cmd)
    elif op == "shell":
        container = dmenu_show("Container", containermap[pod])
        cmd = terminal(
            "k8s logs - %s - %s" % (pod, cluster),
            "kubectl --context=%s exec -it %s -c %s sh"
            % (cluster, pod, container),
        )
        logger.debug("k8s" + str(cmd))
        qtile.spawn(cmd)


def switch_wifi(qtile):
    pass


def set_volume(qtile):
    clients = dict(
        [
            (
                x["properties"]["application.name"],
                x["index"]
                # x["properties"].get("application.process.id", None),
            )
            for x in json.loads(pactl("--format=json", "list", "sink-inputs"))
        ]
    )
    client = dmenu_show("Sink-inputs:", list(clients.keys()))
    volume = dmenu_show("Volumes:", list([str(x) for x in range(0, 201, 10)]))
    pactl(
        "--format=json", "set-sink-input-volume", clients[client], f"{volume}%"
    )


def switch_pulse_inputs(qtile):
    source_outputs = dict(
        [
            (
                "%s - %s" % (x["properties"]["application.name"], x["index"]),
                x
                # x["properties"].get("application.process.id", None),
            )
            for x in json.loads(
                pactl("--format=json", "list", "source-outputs")
            )
        ]
    )
    source_output = dmenu_show("source-outputs:", list(source_outputs.keys()))
    if not source_output:
        return

    sources = dict(
        [
            (x["properties"]["device.product.name"], x["index"])
            for x in json.loads(pactl("--format=json", "list", "sources"))
        ]
    )
    source = dmenu_show("sources:", list(sources.keys()))
    pactl(
        "--format=json",
        "move-source-output",
        source_outputs[source_output]["index"],
        sources[source],
    )


def switch_pulse_outputs(qtile):
    clients = dict(
        [
            (
                "%s - %s" % (x["properties"]["application.name"], x["index"]),
                x
                # x["properties"].get("application.process.id", None),
            )
            for x in json.loads(pactl("--format=json", "list", "sink-inputs"))
        ]
    )
    client = dmenu_show("Sink-inputs:", list(clients.keys()))
    if not client:
        return

    sinks = dict(
        [
            (x["properties"]["device.product.name"], x["index"])
            for x in json.loads(pactl("--format=json", "list", "sinks"))
        ]
    )
    sink = dmenu_show("Sinks:", list(sinks.keys()))
    pactl(
        "--format=json",
        "move-sink-input",
        clients[client]["index"],
        sinks[sink],
    )


def record_window(qtile):
    qtile.current_window.id
    record_window()


def powermenu(qtile):
    option = dmenu_show("Powemenu:", ["quit", "restart", "shutdown"])
