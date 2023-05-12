from . import RedisKeys, AccessLevel
from app.model.config import Models

DEFAULT_ACCESS_LEVEL = AccessLevel.GUEST
DEFAULT_CONVERSATION = []
DEFAULT_MODEL = Models.GPT3_5_TURBO

DEFAULT_NEW_USER = {
    RedisKeys.User.ACCESS_LEVEL: DEFAULT_ACCESS_LEVEL,
    RedisKeys.User.CONVERSATION: DEFAULT_CONVERSATION,
    RedisKeys.User.LOCAL_MODEL: DEFAULT_MODEL.name,
}
