from app.constants.paths import CONFIG_FILE_PATH
from app.constants import AccessLevel

import configparser
import dotenv
import os

from loguru import logger


logger.debug('Loading settings...')
dotenv.load_dotenv()

__RAW_SETTINGS = configparser.ConfigParser()
__RAW_SETTINGS.read(CONFIG_FILE_PATH)

ENVIRONMENT = {
    'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY', ''),
    'TELEGRAM_TOKEN': os.environ.get('TELEGRAM_TOKEN', ''),
    'REDIS_PASSWORD': os.environ.get('REDIS_PASSWORD', '')
}

__RAW_SETTINGS.set('global', 'telegram_token', ENVIRONMENT['TELEGRAM_TOKEN'])
__RAW_SETTINGS.set('global', 'openai_token', ENVIRONMENT['OPENAI_API_KEY'])
__RAW_SETTINGS.set('redis', 'redis_password', ENVIRONMENT['REDIS_PASSWORD'])

MAINTENANCE_MODE = __RAW_SETTINGS.getboolean('global', 'maintenance_mode', fallback=False)
TELEGRAM_TOKEN = __RAW_SETTINGS.get('global', 'telegram_token', fallback=None)
OPENAI_TOKEN = __RAW_SETTINGS.get('global', 'openai_token', fallback=None)

REDIS_HOST = __RAW_SETTINGS.get('redis', 'redis_host', fallback='localhost')
REDIS_PORT = __RAW_SETTINGS.getint('redis', 'redis_port', fallback=6379)
REDIS_DB_INDEX = __RAW_SETTINGS.getint('redis', 'redis_db_index', fallback=0)
REDIS_PASSWORD = __RAW_SETTINGS.get('redis', 'redis_password', fallback=None)

DEFAULT_ACCESS_LEVEL = __RAW_SETTINGS.getint('access', 'default_access_level', fallback=0)
MIN_BOT_ACCESS_LEVEL = __RAW_SETTINGS.getint('access', 'min_bot_access_level', fallback=0)

assert TELEGRAM_TOKEN is not None and TELEGRAM_TOKEN != '', 'Telegram token is not set!'
assert OPENAI_TOKEN is not None and OPENAI_TOKEN != '', 'OpenAI token is not set!'
assert REDIS_PASSWORD is not None and REDIS_PASSWORD != '', 'Redis password is not set!'
assert DEFAULT_ACCESS_LEVEL < AccessLevel.ADMIN, 'Default access level cannot equal or be higher than admin access level!'

logger.info('Settings loaded and validated')