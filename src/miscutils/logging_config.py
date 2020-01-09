"""Default logging configuration for struclog."""

from enum import IntEnum, Enum, auto
import logging
import logging.config
import sys
from typing import Iterable

import structlog

TEXT_LOG_FORMAT = "[%(levelname)s %(filename)s:%(funcName)s:%(lineno)s] %(message)s"
VERBOSE_LEVELS = [logging.WARNING, logging.INFO, logging.DEBUG]


class LogFormat(Enum):
    """Format to write logs in."""

    JSON = auto()
    TEXT = auto()


class Verbosity(IntEnum):
    """Verbosity level for logging. The higher the level the more logging we do."""

    WARNING = 0
    INFO = 1
    DEBUG = 2
    MAX = 3

    def level(self) -> int:
        """
        Get the `logging` level for this verbosity.

        :return: logging level.
        """
        v = self.value
        return VERBOSE_LEVELS[v] if v < len(VERBOSE_LEVELS) else VERBOSE_LEVELS[-1]

def add_line_no(logger, method_name, event_dict):
    """
    Add the line number to the event dict.
    """
    record = event_dict.get("_record")
    if record is not None:
        event_dict["lineno"] = record.lineno
    return event_dict

def add_file_name(logger, method_name, event_dict):
    """
    Add the file name to the event dict.
    """
    record = event_dict.get("_record")
    if record is not None:
        event_dict["filename"] = record.filename
    return event_dict


pre_chain = [
    add_line_no,
    add_file_name,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.processors.UnicodeDecoder(),
]


def default_logging(
    verbosity: int,
    log_format: LogFormat = LogFormat.TEXT,
    external_logs: Iterable[str] = None,
    override_logs: Iterable[str] = None,
) -> None:
    """
    Configure structlog based on the given parameters.

    Logging will be done to stdout.

    :param verbosity: Amount of verbosity to use.
    :param log_format: Format to logs should be written in.
    :param external_logs: External modules that should have logging turned down unless verbosity is
        set to highest level.
    :param override_logs: Loggers that need to have their handlers overridden.
    """
    level = Verbosity(verbosity).level()

    if log_format == LogFormat.TEXT:
        logging.basicConfig(level=level, stream=sys.stdout, format=TEXT_LOG_FORMAT)
        structlog.configure(
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
            processors=pre_chain,
        )
    elif log_format == LogFormat.JSON:
        structlog.configure(
            context_class=structlog.threadlocal.wrap_dict(dict),
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
            processors=[structlog.stdlib.filter_by_level]
            + pre_chain
            + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        )

        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(), foreign_pre_chain=pre_chain
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.addHandler(handler)
        root_logger.setLevel(level)

        # Some loggers have existing handlers that need to be overridden
        if override_logs:
            for log_name in override_logs:
                access_logger = logging.getLogger(log_name)
                access_logger.handlers.clear()
                access_logger.addHandler(handler)
                access_logger.setLevel(level)

    # Unless the user specifies higher verbosity than we have levels, turn down the log level
    # for external libraries.
    if external_logs and verbosity < Verbosity.MAX:
        # Turn down logging for modules outside this project.
        for logger in external_logs:
            logging.getLogger(logger).setLevel(logging.WARNING)
