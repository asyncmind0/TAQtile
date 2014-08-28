from libqtile import widget


class MultiScreenGroupBox(widget.GroupBox):
    def __init__(self, **config):
        widget.GroupBox.__init__(self, **config)
        self.namemap = config.get('namemap', {})

    def calculate_width(self):
        width = 0
        for g in self.qtile.groups:
            gtext = self.get_label(g.name)
            if not gtext:
                continue
            width += self.label_width([gtext])
        return width

    def label_width(self, labels):
        width, height = self.drawer.max_layout_size(
            [i for i in labels],
            self.font,
            self.fontsize
        )
        return width + self.padding_x * 2 + self.margin_x * 2 + \
            self.borderwidth * 2

    def get_label(self, group):
        return self.namemap.get(group)

    def draw(self):
        self.drawer.clear(self.background or self.bar.background)

        offset = 0
        for i, g in enumerate(self.qtile.groups):
            gtext = self.get_label(g.name)
            #log.debug(gtext)
            if not gtext:
                continue

            is_block = (self.highlight_method == 'block')

            bw = self.label_width([gtext])
            if g.screen:
                if self.bar.screen.group.name == g.name:
                    if self.qtile.currentScreen == self.bar.screen:
                        border = self.this_current_screen_border
                    else:
                        border = self.this_screen_border
                else:
                    border = self.other_screen_border
            elif self.group_has_urgent(g) and \
                    self.urgent_alert_method in ('border', 'block'):
                border = self.urgent_border
                if self.urgent_alert_method == 'block':
                    is_block = True
            else:
                border = self.background or self.bar.background

            if self.group_has_urgent(g) and self.urgent_alert_method == "text":
                text = self.urgent_text
            elif g.windows:
                text = self.active
            else:
                text = self.inactive

            self.drawbox(
                self.margin_x + offset,
                gtext,
                border,
                text,
                self.rounded,
                is_block,
                bw - self.margin_x * 2 - self.padding_x * 2
            )
            offset += bw
        self.drawer.draw(self.offset, self.width)
