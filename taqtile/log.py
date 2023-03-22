from libqtile.log_utils import init_log as default_init_log
import logging

logger = logging.getLogger("libqtile")


class NoParsingFilter(logging.Filter):
    def filter(self, record):
        return ".config/qtile" in record.pathname
        # return not record.getMessage().startswith('parsing')


def init_log(**kwargs):
    global logger
    default_init_log(
        log_path="~/.%s.user.log",
        # logger=logger,
        **kwargs
    )

    logger.addFilter(NoParsingFilter())
    return logger
