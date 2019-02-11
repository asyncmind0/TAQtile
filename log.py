from libqtile.log_utils import init_log as default_init_log
import logging

logger = logging.getLogger("libqtile")


def init_log(**kwargs):
    global logger
    logger = default_init_log(
        log_path='~/.%s.user.log',
        #logger=logger,
        **kwargs
    )
    return logger
