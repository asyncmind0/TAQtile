from libqtile import widget


class PriorityNotify(widget.base.ThreadedPollText):
    defaults = [
        ("graph_color", "18BAEB", "Graph color"),
        ("fill_color", "1667EB.3", "Fill color for linefill graph"),
        ("border_color", "215578", "Widget border color"),
        ("border_width", 2, "Widget border width"),
        ("margin_x", 3, "Margin X"),
        ("margin_y", 3, "Margin Y"),
        ("samples", 100, "Count of graph samples."),
        ("frequency", 1, "Update frequency in seconds"),
        ("type", "linefill", "'box', 'line', 'linefill'"),
        ("line_width", 3, "Line width"),
        ("start_pos", "bottom", "Drawer starting position ('bottom'/'top')"),
        ("background", "18BAEB", "Widget background color"),
    ]

    def __init__(self, width=100, **config):
        widget.base.ThreadedPollText.__init__(self, **config)
        self.add_defaults(PriorityNotify.defaults)
