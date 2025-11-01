import logging
from enum import Enum

from resumex.config import LOG_LEVEL

LOG_FORMAT_DEBUG = "%(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"


class LogLevels(Enum):
    info = "INFO"
    warn = "WARN"
    error = "ERROR"
    debug = "DEBUG"


def configure_logging() -> None:
    log_level = str(LOG_LEVEL).upper()  # cast to string
    log_levels = [level.value for level in LogLevels]

    if log_level not in log_levels:
        # we use error as the default log level
        logging.basicConfig(level=LogLevels.error.value)
        return

    if log_level == LogLevels.debug.value:
        logging.basicConfig(level=log_level, format=LOG_FORMAT_DEBUG)
        return

    logging.basicConfig(level=log_level)

    # sometimes the slack client can be too verbose
    logging.getLogger("slack_sdk.web.base_client").setLevel(logging.CRITICAL)
