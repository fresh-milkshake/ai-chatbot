from dataclasses import dataclass

from config.general import GLOBAL_DEFAULT_MODEL

# Redis parameters
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB_INDEX = 0

REDIS_USERS_KEY = 'users'
REDIS_USER_ACCESS_LEVEL_KEY = 'access_level'
REDIS_USER_CONVERSATION_KEY = 'conversation'
REDIS_USER_UNIQUE_ID_KEY = 'unique_id'
REDIS_USER_LANGUAGE_CODE = 'language_code'
REDIS_USER_LOCAL_MODEL = 'local_model'


# User defaults
@dataclass
class AccessLevel:
    GUEST = 0
    USER = 1
    PRIVILEGED_USER = 2
    MODERATOR = 3
    ADMIN = 4

    LEVELS = [GUEST, USER, PRIVILEGED_USER, MODERATOR, ADMIN]

    _locales = {
        'en': {
            GUEST: 'Guest',
            USER: 'User',
            PRIVILEGED_USER: 'Privileged user',
            MODERATOR: 'Moderator',
            ADMIN: 'Admin',
        },
        'ru': {
            GUEST: 'Гость',
            USER: 'Пользователь',
            PRIVILEGED_USER: 'Привилегированный пользователь',
            MODERATOR: 'Модератор',
            ADMIN: 'Администратор',
        },
    }

    @classmethod
    def get_access_level(cls, access_level: int, locale: str = 'ru') -> str:
        match access_level:
            case cls.GUEST:
                return cls._locales[locale][cls.GUEST]
            case cls.USER:
                return cls._locales[locale][cls.USER]
            case cls.PRIVILEGED_USER:
                return cls._locales[locale][cls.PRIVILEGED_USER]
            case cls.MODERATOR:
                return cls._locales[locale][cls.MODERATOR]
            case x if x >= cls.ADMIN:
                return cls._locales[locale][cls.ADMIN]


DEFAULT_ACCESS_LEVEL = AccessLevel.GUEST
DEFAULT_CONVERSATION = []

DEFAULT_NEW_USER = {
    REDIS_USER_ACCESS_LEVEL_KEY: DEFAULT_ACCESS_LEVEL,
    REDIS_USER_CONVERSATION_KEY: DEFAULT_CONVERSATION,
    REDIS_USER_LOCAL_MODEL: GLOBAL_DEFAULT_MODEL
}
