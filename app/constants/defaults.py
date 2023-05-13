from app.constants import RedisKeys, AccessLevel
from app.constants.models import AvailableModels

DEFAULT_ACCESS_LEVEL = AccessLevel.GUEST
DEFAULT_CONVERSATION = []
DEFAULT_MODEL = AvailableModels.GPT3_5_TURBO

DEFAULT_NEW_USER = {
    RedisKeys.User.ACCESS_LEVEL: DEFAULT_ACCESS_LEVEL,
    RedisKeys.User.CONVERSATION: DEFAULT_CONVERSATION,
    RedisKeys.User.LOCAL_MODEL: DEFAULT_MODEL.name,
}

