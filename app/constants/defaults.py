from app.constants import DatabaseKeys
from app.constants.models import (
    AvailableModels,
    DEFAULT_TEMPERATURE,
)
from app.startup import DEFAULT_ACCESS_LEVEL


DEFAULT_CONVERSATION = []
DEFAULT_MODEL = AvailableModels.latest_free()
DEFAULT_TEMPERATURE = DEFAULT_TEMPERATURE

DEFAULT_NEW_USER = {
    DatabaseKeys.User.ACCESS_LEVEL: DEFAULT_ACCESS_LEVEL,
    DatabaseKeys.User.CONVERSATION: DEFAULT_CONVERSATION,
    DatabaseKeys.User.CHOSEN_MODEL: DEFAULT_MODEL.name,
}

RATE_LIMIT_PAUSE = 2
