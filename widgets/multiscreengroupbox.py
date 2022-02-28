from libqtile import widget
from system import get_current_screen
from log import logger
from themes import default_params


class _MultiScreenGroupBox(widget.GroupBox):
    def __init__(self, **config):
        self.screen = config.pop("screen", {})
        super().__init__(**config)
        self.center_aligned = False

    def _box_width(self, groups):
        width, height = self.drawer.max_layout_size(
            [self.get_label(i.name) for i in groups], self.font, self.fontsize
        )
        return (
            width
            + self.padding_x * 2
            + self.margin_x * 2
            + self.borderwidth * 2
        )

    def _get_label(self, group):
        return self.namemap.get(group)

    @property
    def groups(self):
        grp0 = []
        grps = super().groups
        for group in grps:
            if group.name.isdigit():
                if len(group.name) == 1:
                    mon = 0
                else:
                    mon = int(group.name[0])
                if mon != self.screen:
                    continue
            # logger.debug(
            #    "Group screen: %s: GroupBox screen %s"
            #    % (group.screen.index, self.screen)
            # )
            if group.screen and group.screen.index != self.screen:
                continue
            grp0.append(group)
        return grp0


class MultiScreenGroupBox(_MultiScreenGroupBox):
    def __init__(self, **config):
        groupbox_params = default_params(
            padding=2,
            urgent_alert_method="text",
            rounded=False,
            border_focus="#FFFFFF",
            is_line=False,
            center_aligned=True,
            hide_unused=True,
            spacing=1,
        )
        groupbox_params.update(config)

        super().__init__(**groupbox_params)


class __MultiScreenGroupBox(widget.GroupBox):
    pass
