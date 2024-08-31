import sys

from app.constants.logging import (LOG_FILE_ROTATION, LOG_FILE_COMPRESSION, LOGGING_FORMAT_FILE,
                                   LOGGING_LEVEL_FOR_FILE, LOGGING_FORMAT_CONSOLE, LOGGING_LEVEL_FOR_CONSOLE)
from app.constants.paths import LOG_FILE_PATH
from loguru import logger


# Setup logger
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
