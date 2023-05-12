import pathlib

ROOT_MODULE = 'app'

PROJECT_DIR = pathlib.Path(__file__).parent.parent.parent
PROJECT_NAME = PROJECT_DIR.name

DATA_DIR = PROJECT_DIR / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)
USERS_DATA_FILE_NAME = 'users.json'
USERS_DATA_PATH = DATA_DIR / USERS_DATA_FILE_NAME

REPORTS_PATH = DATA_DIR / 'reports'

CONFIG_FILE_NAME = 'config.ini'
CONFIG_FILE_PATH = PROJECT_DIR / CONFIG_FILE_NAME
