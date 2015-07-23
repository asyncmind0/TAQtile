from libqtile import widget


class MultiScreenGroupBox(widget.GroupBox):
    def __init__(self, **config):
        widget.GroupBox.__init__(self, **config)
        self.namemap = config.get('namemap', {})
        self.center_aligned = False

    def box_width(self, groups):
        width, height = self.drawer.max_layout_size(
            [self.get_label(i.name) for i in groups],
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
            is_block = (self.highlight_method == 'block')
            gtext = self.get_label(g.name)
            #log.debug(gtext)
            if not gtext:
                continue

            bw = self.box_width([g])

            if self.group_has_urgent(g) and self.urgent_alert_method == "text":
                text_color = self.urgent_text
            elif g.windows:
                text_color = self.active
            else:
                text_color = self.inactive

            if g.screen:
                if self.highlight_method == 'text':
                    border = self.bar.background
                    text_color = self.this_current_screen_border
                else:
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

            self.drawbox(
                self.margin_x + offset,
                self.get_label(g.name),
                border,
                text_color,
                self.rounded,
                is_block,
                bw - self.margin_x * 2 - self.padding_x * 2
            )
            offset += bw
        self.drawer.draw(offsetx=self.offset, width=self.width)
