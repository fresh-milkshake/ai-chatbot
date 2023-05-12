import sys

from experiments.config import *
from loguru import logger


def setup_logger():
    logger.remove()
    logger.add(LOG_FILE_PATH,
               rotation=LOG_FILE_ROTATION,
                compression=LOG_FILE_COMPRESSION,
                colorize=True,
                format=LOGGING_FORMAT_FILE,
                enqueue=True,
                backtrace=True,
                diagnose=True,
                level=LOGGING_LEVEL_FOR_FILE)

    logger.add(sys.stdout,
            colorize=True,
                format=LOGGING_FORMAT_CONSOLE,
                enqueue=True,
                backtrace=True,
                diagnose=True,
                level=LOGGING_LEVEL_FOR_CONSOLE)