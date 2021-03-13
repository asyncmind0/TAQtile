from libqtile import widget
from system import get_current_screen
from log import logger


class MultiScreenGroupBox(widget.GroupBox):
    def __init__(self, **config):
        widget.GroupBox.__init__(self, **config)
        self.namemap = config.get("namemap", {})
        self.center_aligned = False

    def box_width(self, groups):
        width, height = self.drawer.max_layout_size(
            [self.get_label(i.name) for i in groups], self.font, self.fontsize
        )
        return (
            width
            + self.padding_x * 2
            + self.margin_x * 2
            + self.borderwidth * 2
        )

    def get_label(self, group):
        return self.namemap.get(group)

    def draw(self):
        self.drawer.clear(self.background or self.bar.background)
        offset = 0
        for i, g in enumerate(self.groups):
            gtext = self.get_label(g.name)
            # logger.debug(gtext)
            if not gtext:
                continue
            to_highlight = False
            is_block = self.highlight_method == "block"
            is_line = self.highlight_method == "line"

            bw = self.box_width([g])

            if self.group_has_urgent(g) and self.urgent_alert_method == "text":
                text_color = self.urgent_text
            elif g.windows:
                text_color = self.active
            else:
                text_color = self.inactive

            if g.screen:
                if self.highlight_method == "text":
                    border = self.bar.background
                    text_color = self.this_current_screen_border
                else:
                    if self.bar.screen.group.name == g.name:
                        if get_current_screen(self.qtile) == self.bar.screen:
                            border = self.this_current_screen_border
                            to_highlight = True
                        else:
                            border = self.this_screen_border
                    else:
                        border = self.other_screen_border
            elif self.group_has_urgent(g) and self.urgent_alert_method in (
                "border",
                "block",
                "line",
            ):
                border = self.urgent_border
                if self.urgent_alert_method == "block":
                    is_block = True
                elif self.urgent_alert_method == "line":
                    is_line = True
            else:
                border = self.background or self.bar.background

            self.drawbox(
                self.margin_x + offset,
                gtext,
                # g.name,
                border,
                text_color,
                highlight_color=self.highlight_color,
                width=bw - self.margin_x * 2 - self.padding_x * 2 - 1,
                rounded=self.rounded,
                block=is_block,
                line=is_line,
                highlighted=to_highlight,
            )
            offset += bw
        self.drawer.draw(offsetx=self.offset, width=self.width)
