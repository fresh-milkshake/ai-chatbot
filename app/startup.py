from app.constants.paths import CONFIG_FILE_PATH
from app.constants import AccessLevel

import toml
import dotenv
import os
from typing import Dict, Any

from loguru import logger


CONFIG_TEMPLATE = """
[global]
maintenance_mode = false
telegram_bot_token = { env = "TELEGRAM_BOT_TOKEN" }

[models]
# openai_api_key = { env = "OPENAI_API_KEY" }
# ollama_api_url = { env = "OLLAMA_API_URL" } # TODO

[database]
provider = "sqlite"
path = "sqlite.db"

# Uncomment and configure the database you want to use
# [database]
# type = "mongodb"
# host = "localhost"
# port = 27017
# username = { env = "MONGODB_USERNAME" }
# password = { env = "MONGODB_PASSWORD" }
# database_name = "mongodb"

# [database]
# type = "postgres"
# host = "localhost"
# port = 5432
# username = { env = "POSTGRES_USERNAME" }
# password = { env = "POSTGRES_PASSWORD" }
# database_name = "postgres"

# [database]
# type = "mysql"
# host = "localhost"
# port = 3306
# username = { env = "MYSQL_USERNAME" }
# password = { env = "MYSQL_PASSWORD" }
# database_name = "mysql"

[access]
default_user_level = 0
minimum_required_level = 0
maintenance_access_level = 3
admin_user_id = { env = "ADMIN_USER_ID" }
"""

ENV_TELEGRAM_BOT_TOKEN = "telegram_bot_token"


def load_config() -> Dict[str, Any]:
    logger.debug("Loading configuration...")
    dotenv.load_dotenv()

    if not CONFIG_FILE_PATH.exists():
        logger.debug("Creating configuration file...")
        CONFIG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE_PATH.write_text(CONFIG_TEMPLATE)
        logger.critical(
            f"Configuration file not found at {CONFIG_FILE_PATH}! Created a template configuration file for you."
        )
        exit(1)

    if not CONFIG_FILE_PATH.read_text().strip():
        logger.critical("Configuration file is empty!")
        exit(1)

    return toml.load(CONFIG_FILE_PATH)


def load_environment_variables(raw_config: Dict[str, Any]) -> Dict[str, Any]:
    env_vars = {}
    for section in raw_config.values():
        if isinstance(section, dict):
            for key, value in section.items():
                if isinstance(value, dict) and "env" in value:
                    env_var = os.getenv(value["env"])
                    if env_var is not None:
                        env_vars[key] = env_var
                    else:
                        logger.warning(
                            f"Environment variable {value['env']} not found for {key}"
                        )
    logger.debug("Environment variables loaded")
    return env_vars


def validate_config(config: Dict[str, Any]) -> None:
    if not config["TELEGRAM_BOT_TOKEN"]:
        logger.critical("Telegram bot token is not set!")
        exit(1)

    if config["DEFAULT_ACCESS_LEVEL"] > AccessLevel.ADMIN:
        logger.critical("Default user level cannot be higher than admin access level!")
        exit(1)

    logger.debug("Telegram bot token and access levels validated")


# Load and process configuration
__RAW_CONFIG = load_config()
ENVIRONMENT_VARIABLES = load_environment_variables(__RAW_CONFIG)

# Global settings
MAINTENANCE_MODE = __RAW_CONFIG.get("global", {}).get("maintenance_mode", False)
TELEGRAM_BOT_TOKEN = ENVIRONMENT_VARIABLES.get(ENV_TELEGRAM_BOT_TOKEN)

# Database settings
DATABASE_CONFIG: Dict[str, Any] = __RAW_CONFIG.get("database", {})
for key, value in DATABASE_CONFIG.items():
    if isinstance(value, dict) and "env" in value:
        DATABASE_CONFIG[key] = ENVIRONMENT_VARIABLES.get(key, value["env"])

# Access settings
DEFAULT_ACCESS_LEVEL = __RAW_CONFIG.get("access", {}).get(
    "default_access_level", AccessLevel.GUEST
)
MIN_REQUIRED_ACCESS_LEVEL = __RAW_CONFIG.get("access", {}).get(
    "min_required_access_level", AccessLevel.GUEST
)
MAINTENANCE_ACCESS_LEVEL = __RAW_CONFIG.get("access", {}).get(
    "maintenance_access_level", AccessLevel.MODERATOR
)
ADMIN_USER_ID = __RAW_CONFIG.get("access", {}).get(
    "admin_user_id", ENVIRONMENT_VARIABLES.get("ADMIN_USER_ID")
)

# Validate configuration
validate_config(locals())

logger.info("Configuration loaded and validated")
