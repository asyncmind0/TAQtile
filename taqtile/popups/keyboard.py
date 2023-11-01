from os.path import expanduser
from qtile_extras.popup.toolkit import (
    PopupRelativeLayout,
    PopupImage,
    PopupText,
    PopupGridLayout
)
from libqtile.command import lazy

keys = [
    ["Esc", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"],
    ["~\n`", "!\n1", "@\n2", "#\n3", "$\n4", "%\n5", "^\n6", "&\n7", "*\n8", "(\n9", ")\n0", "_\n-", "+\n=", "Backspace"],
    ["Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "{\n[", "}\n]", "|\n\\"],
    ["Caps Lock", "A", "S", "D", "F", "G", "H", "J", "K", "L", ":\n;", "\"\n'", "Enter"],
    ["Shift", "Z", "X", "C", "V", "B", "N", "M", "<\n,", ">\n.", "?\n/", "Shift"],
    ["Ctrl", "Win", "Alt", "Space", "Alt", "Win", "Menu", "Ctrl"]
]


def show_keyboard(qtile):
    controls = []
    for i,row in enumerate(keys):
        for j,key in enumerate(row):
            controls.append(PopupText(
                key,row=i,
                col=j,
            width=1,
            height=5,
                            ))

    layout = PopupGridLayout(
        qtile,
        rows=6,
        cols=14,
        controls=controls,
        close_on_click=False,
        width=500,
        height=400,
    )

    layout.show()
