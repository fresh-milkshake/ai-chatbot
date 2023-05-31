LOGGING_FORMAT_CONSOLE = '<cyan>{time:YYYY-MM-DD HH:mm:ss.SSS}</cyan> ' \
                        '<level>{level: <8}</level>' \
                        '<green>{file.name: <12}:{line: <6}</green>' \
                        '<level>{message}</level>'
LOGGING_FORMAT_FILE = '{time:YYYY-MM-DD HH:mm:ss.SSS} ' \
                        '{level: <8}' \
                        '{file.name: <12}:{line: <6}' \
                        '{message}'

AVAILABLE_LOGGING_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
DEFAULT_LOGGING_LEVEL = AVAILABLE_LOGGING_LEVELS[1]
LOGGING_LEVEL_FOR_FILE = 'DEBUG' or DEFAULT_LOGGING_LEVEL
LOGGING_LEVEL_FOR_CONSOLE = 'DEBUG' or DEFAULT_LOGGING_LEVEL

LOG_FILE_COMPRESSION = 'zip'
LOG_FILE_ROTATION = '500 MB'
LOGS_FILE_NAME_FORMAT = '{time:YYYY-MM-DD}'