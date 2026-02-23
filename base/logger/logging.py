import logging
import sys
import os
from typing import Any

SUCCESS_LEVELV_NUM = 25
logging.addLevelName(SUCCESS_LEVELV_NUM, "SUCCESS")

class ManagerLogger(logging.Logger):
    def success(self, message: str, *args: Any, **kwargs: Any) -> None:
        if self.isEnabledFor(SUCCESS_LEVELV_NUM):
            self._log(SUCCESS_LEVELV_NUM, message, args, **kwargs)

logging.setLoggerClass(ManagerLogger)

class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    blue = "\x1b[34;20m"
    green = "\x1b[32;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    format_str = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: blue + format_str + reset,
        SUCCESS_LEVELV_NUM: green + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno, self.grey + self.format_str + self.reset)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

def setup_logger() -> ManagerLogger:

    logger = logging.getLogger("Manager")
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(CustomFormatter())

    if not logger.handlers:
        logger.addHandler(console_handler)

    return logger

logger: ManagerLogger = setup_logger()