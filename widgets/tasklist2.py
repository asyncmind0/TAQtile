from libqtile import widget


class TaskList2(widget.TaskList):
    def draw_icon(self, window, offset):
        if not getattr(window, 'icons', None):
            return
        surface = self.get_window_icon(window)
                     
        if not surface:
            return

        x = offset + self.padding_x + self.borderwidth  # + self.margin_x - 4
        y = self.padding_y + self.borderwidth + 2

        self.drawer.ctx.save()
        self.drawer.ctx.translate(x, y)
        self.drawer.ctx.set_source(surface)
        self.drawer.ctx.paint()
        self.drawer.ctx.restore()
