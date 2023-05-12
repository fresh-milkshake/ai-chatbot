from app.constants.paths import CONFIG_FILE_PATH

import configparser

SETTINGS = configparser.ConfigParser()
SETTINGS.read(CONFIG_FILE_PATH)

MAINTENANCE_MODE = SETTINGS.getboolean('global', 'maintenance_mode', fallback=False)
TELEGRAM_TOKEN = SETTINGS.get('global', 'telegram_token', fallback=None)

REDIS_HOST = SETTINGS.get('redis', 'redis_host', fallback='localhost')
REDIS_PORT = SETTINGS.getint('redis', 'redis_port', fallback=6379)
REDIS_DB_INDEX = SETTINGS.getint('redis', 'redis_db_index', fallback=0)
REDIS_PASSWORD = SETTINGS.get('redis', 'redis_password', fallback=None)

DEFAULT_ACCESS_LEVEL = SETTINGS.getint('access', 'default_access_level', fallback=0)
MIN_BOT_ACCESS_LEVEL = SETTINGS.getint('access', 'min_bot_access_level', fallback=0)
