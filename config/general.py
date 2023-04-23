import os
from dataclasses import dataclass

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
@dataclass
class Models:
    MODEL_GPT35TURBO0301 = 'gpt-3.5-turbo-0301'
    MODEL_GPT35TURBO = 'gpt-3.5-turbo'
    # MODEL_GPT4 = 'gpt-4'


MODEL_NAME = Models.MODEL_GPT35TURBO

# Model answer formatting parameters
DIVIDER = '=' * 50
WRAP_LENGTH = 80

# Telegram bot parameters
USERS_PER_PAGE = 5
