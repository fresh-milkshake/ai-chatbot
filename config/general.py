import os
from dataclasses import dataclass
from collections import namedtuple

from config import AccessLevel

# Paths
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_NAME = '' or os.path.basename(PROJECT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, 'data')
if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

USERS_DATA_FILE_NAME = 'users.json'
USERS_DATA_PATH = os.path.join(DATA_DIR, USERS_DATA_FILE_NAME)
REPORTS_PATH = os.path.join(DATA_DIR, 'reports')

# Model parameters
_DEFAULT_TEMPERATURE = 0.7
_DEFAULT_MIN_ACCESS_LEVEL = AccessLevel.USER
Model = namedtuple('Model', ['name', 'temperature', 'min_access_level'],
                   defaults=[None, _DEFAULT_TEMPERATURE, _DEFAULT_MIN_ACCESS_LEVEL])


@dataclass
class Models:
    GPT3_5_TURBO = Model('gpt-3.5-turbo', _DEFAULT_TEMPERATURE, AccessLevel.USER)
    GPT4 = Model('gpt-4', _DEFAULT_TEMPERATURE, AccessLevel.PRIVILEGED_USER)
    GPT4_32K = Model('gpt-4-32k', _DEFAULT_TEMPERATURE, AccessLevel.PRIVILEGED_USER)

    TEXT_DAVINCI_003 = Model('text-davinci-003', _DEFAULT_TEMPERATURE, AccessLevel.USER)
    CODE_DAVINCI_002 = Model('code-davinci-002', _DEFAULT_TEMPERATURE, AccessLevel.USER)

    ALL = [GPT3_5_TURBO, GPT4, GPT4_32K, TEXT_DAVINCI_003, CODE_DAVINCI_002]


GLOBAL_DEFAULT_MODEL = Models.GPT3_5_TURBO

# Model answer formatting parameters
DIVIDER = '=' * 50
WRAP_LENGTH = 80

# Telegram bot parameters
USERS_PER_PAGE = 5
