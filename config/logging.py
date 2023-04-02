import os

from config.general import PROJECT_DIR, PROJECT_NAME

# Logging parameters

LOGGING_FORMAT_CONSOLE = '<cyan>{time:YYYY-MM-DD HH:mm:ss.SSS}</cyan> ' \
                        '<level>{level: <8}</level>' \
                        '<green>{file.name: <9}:{line: <6}</green>' \
                        '<level>{message}</level>'
LOGGING_FORMAT_FILE = '{time:YYYY-MM-DD HH:mm:ss.SSS} ' \
                        '{level: <8}' \
                        '{file.name: <9}:{line: <6}' \
                        '{message}'

AVALIABLE_LOGGING_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
DEFAULT_LOGGING_LEVEL = AVALIABLE_LOGGING_LEVELS[1]
LOGGING_LEVEL_FOR_FILE = 'DEBUG' or DEFAULT_LOGGING_LEVEL
LOGGING_LEVEL_FOR_CONSOLE = 'DEBUG' or DEFAULT_LOGGING_LEVEL

LOG_FILE_COMPRESSION = 'zip'
LOG_FILE_ROTATION = '500 MB'
LOGS_FILE_NAME_FORMAT = '{time:YYYY-MM-DD}'

LOG_FILE_NAME = f'{PROJECT_NAME}-{LOGS_FILE_NAME_FORMAT}.log'
LOGS_DIR_NAME = 'logs'
LOGS_DIR = os.path.join(PROJECT_DIR, LOGS_DIR_NAME)
if not os.path.exists(LOGS_DIR):
    os.mkdir(LOGS_DIR)

LOG_FILE_PATH = os.path.join(LOGS_DIR, LOG_FILE_NAME)