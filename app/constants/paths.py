import pathlib
from app.constants.logging import LOGS_FILE_NAME_FORMAT

from loguru import logger

ROOT_MODULE = "app"

TMP_FILE_NAME = "dump.json"

PROJECT_DIR = pathlib.Path(__file__).parent.parent.parent
PROJECT_NAME = PROJECT_DIR.name

DATA_DIR = PROJECT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
USERS_DATA_FILE_NAME = "users.json"
USERS_DATA_PATH = DATA_DIR / USERS_DATA_FILE_NAME

REPORTS_PATH = DATA_DIR / "reports"

SUPPORTED_CONFIG_FILE_EXTENSIONS = {".toml", ".ini"}

CONFIG_FILE_EXTENSION = ".toml"
if CONFIG_FILE_EXTENSION not in SUPPORTED_CONFIG_FILE_EXTENSIONS:
    logger.error(
        f"Config file extension {CONFIG_FILE_EXTENSION} is not supported. Available extensions are: {SUPPORTED_CONFIG_FILE_EXTENSIONS}"
    )
    exit(1)

CONFIG_FILE_NAME = "config" + CONFIG_FILE_EXTENSION
CONFIG_FILE_PATH = PROJECT_DIR / CONFIG_FILE_NAME

LOGS_DIR_NAME = "logs"
LOGS_DIR = PROJECT_DIR / LOGS_DIR_NAME
LOGS_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE_NAME = f"{PROJECT_NAME}-{LOGS_FILE_NAME_FORMAT}.log"
LOG_FILE_PATH = LOGS_DIR / LOG_FILE_NAME
