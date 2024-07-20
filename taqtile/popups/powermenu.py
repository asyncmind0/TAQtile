from os.path import expanduser
from qtile_extras.popup.toolkit import (
    PopupRelativeLayout,
    PopupImage,
    PopupText,
)
from libqtile.lazy import lazy


def show_power_menu(qtile):
    controls = [
        PopupImage(
            filename="/usr/share/icons/breeze-dark/actions/24/lock.svg",
            pos_x=0.15,
            pos_y=0.1,
            width=0.1,
            height=0.5,
            mouse_callbacks={"Button1": lazy.spawn(expanduser("~/.bin/lock"))},
        ),
        PopupImage(
            filename="/usr/share/icons/breeze-dark/actions/24/system-suspend.svg",
            pos_x=0.45,
            pos_y=0.1,
            width=0.1,
            height=0.5,
            mouse_callbacks={"Button1": lazy.spawn("/path/to/sleep_cmd")},
        ),
        PopupImage(
            filename="/usr/share/icons/breeze-dark/actions/24/system-shutdown.svg",
            pos_x=0.75,
            pos_y=0.1,
            width=0.1,
            height=0.5,
            highlight="A00000",
            mouse_callbacks={"Button1": lazy.shutdown()},
        ),
        PopupImage(
            filename="/usr/share/icons/breeze-dark/actions/24/system-reboot.svg",
            pos_x=0.105,
            pos_y=0.1,
            width=0.1,
            height=0.5,
            highlight="A00000",
            mouse_callbacks={"Button1": lazy.shutdown()},
        ),
        PopupText(
            text="Lock",
            pos_x=0.1,
            pos_y=0.7,
            width=0.2,
            height=0.2,
            h_align="center",
        ),
        PopupText(
            text="Sleep",
            pos_x=0.4,
            pos_y=0.7,
            width=0.2,
            height=0.2,
            h_align="center",
        ),
        PopupText(
            text="Shutdown",
            pos_x=0.7,
            pos_y=0.7,
            width=0.2,
            height=0.2,
            h_align="center",
        ),
        PopupText(
            text="Restart",
            pos_x=0.4,
            pos_y=0.7,
            width=0.2,
            height=0.2,
            h_align="center",
        ),
    ]

    layout = PopupRelativeLayout(
        qtile,
        width=2200,
        height=200,
        controls=controls,
        background="00000060",
        initial_focus=None,
    )

    layout.show(centered=True)


# keys = [
#    ...
#    Key([mod, "shift"], "q", lazy.function(show_power_menu))
#    ...
# ]
