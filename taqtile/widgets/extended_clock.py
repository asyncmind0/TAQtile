from datetime import datetime

from libqtile import widget

from qtile_extras import widget as extrawidgets
from qtile_extras.popup.toolkit import (
    PopupRelativeLayout,
    PopupText,
    PopupWidget,
)
from qtile_extras.widget.mixins import ExtendedPopupMixin


class ExtendedClock(widget.Clock, ExtendedPopupMixin):
    def __init__(self, **config):
        widget.Clock.__init__(self, **config)
        ExtendedPopupMixin.__init__(self, **config)
        self.add_defaults(ExtendedPopupMixin.defaults)
        self.add_callbacks({"Button1": self.show_popup})

    def _update_popup(self):
        longdate = datetime.now().strftime("%A %d %B %Y")
        self.extended_popup.update_controls(longdate=longdate)


clock_layout = PopupRelativeLayout(
    width=250,
    height=250,
    controls=[
        PopupText(
            name="longdate",
            pos_x=0.1,
            pos_y=0.05,
            width=0.8,
            height=0.05,
            h_align="center",
        ),
        PopupWidget(
            widget=extrawidgets.AnalogueClock(
                second_size=2,
                minute_size=4,
                hour_size=6,
                face_shape="circle",
                face_background="222222",
                face_border_width=4,
            ),
            pos_x=0.05,
            pos_y=0.1,
            width=0.9,
            height=0.9,
        ),
    ],
    background="00000000",
)

extended_clock = ExtendedClock(
    popup_layout=clock_layout,
    popup_hide_timeout=0,
    popup_show_args={"relative_to": 3, "relative_to_bar": True},
)
