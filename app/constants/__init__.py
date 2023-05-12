from . import strings
from . import openai_models


class AccessLevel:
    """
    Access levels for users to manage their permissions, requests per day capacity, etc.

    Attributes:
        GUEST: A guest user.
        USER: A regular user.
        PRIVILEGED_USER: A user with more access, but not allowed to use moderation commands.
        MODERATOR: A moderator.
        ADMIN: An administrator.

    Examples:
        >>> AccessLevel.GUEST
        0
        >>> AccessLevel.USER
        1
        >>> AccessLevel.PRIVILEGED_USER
        2
        >>> AccessLevel.from_string('guest')
        0
        >>> AccessLevel.from_int(1)
        'user'
        >>> AccessLevel.from_string('invalid')
        ValueError: Invalid access level string.
        >>> AccessLevel.from_int(AccessLevel.ADMIN)
        'admin'

    See Also:
        :class:`app.database.data_objects.User` for more information about how access levels are used.
    """

    GUEST = 0
    USER = 1
    PRIVILEGED_USER = 2
    MODERATOR = 3
    ADMIN = 4

    __translations = {
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

    @property
    def all(self) -> list[int]:
        """
        Returns a list of all access levels as integers.

        Returns:
            A list of integers representing all access levels.
        """

        levels = []
        for attribute in dir(self):
            if not attribute.startswith('__') and not callable(getattr(self, attribute)) \
                    and attribute.isupper() and isinstance(getattr(self, attribute), int):
                levels.append(getattr(self, attribute))
        return levels

    @classmethod
    def from_int(cls, access_level: int, locale: str = 'ru') -> str:
        """
        Returns the name of the access level corresponding to the given integer value.

        Args:
            access_level (int): The integer value of the access level.
            locale (str): The locale to use for the access level name. Defaults to 'ru'.

        Returns:
            A string representing the name of the access level corresponding to the given integer value.
        """

        translations = cls.__translations.get(locale, {})
        if access_level in translations:
            return translations[access_level]
        elif access_level <= cls.GUEST:
            return translations[cls.GUEST]
        elif access_level >= cls.ADMIN:
            return translations[cls.ADMIN]
        else:
            raise ValueError(f'Cannot process access level: {access_level}')

    @classmethod
    def from_string(cls, access_level: str, locale: str = 'ru') -> int:
        """
        Returns the integer value of the access level corresponding to the given string value.

        Args:
            access_level (str): The string value of the access level.
            locale (str): The locale to use for the access level name. Defaults to 'ru'.

        Returns:
            An integer representing the access level corresponding to the given string value.

        Raises:
            ValueError: If the given string value does not correspond to a valid access level.
        """

        for level, level_names in cls.__translations[locale].items():
            if access_level.lower() == level_names.lower():
                return level
        raise ValueError(f'Invalid access level string: {access_level}')


class RedisKeys:
    """
    Redis database keys in form of a nested classes with attributes as keys.

    Nested classes are used to group keys by their purpose or by shared parent key.
    For example, all keys related to `users` key are grouped in User class.

    Attributes:
        USERS: Users key
    """

    USERS = 'users'

    class User:
        """
        User keys.

        Attributes:
            ACCESS_LEVEL: Access level
            CONVERSATION: User conversation history
            UNIQUE_ID: Unique user id
            LANGUAGE_CODE: Language code
            LOCAL_MODEL: OpenAI model name
        """

        ACCESS_LEVEL = 'access_level'
        CONVERSATION = 'conversation'
        UNIQUE_ID = 'unique_id'
        LANGUAGE_CODE = 'language_code'
        LOCAL_MODEL = 'local_model'

    class Bot:
        """
        Bot keys.

        Attributes:
            SUCCESSFUL_RESPONSES: Number of successful responses
            FAILED_RESPONSES: Number of failed responses
            RESPONSES_HISTORY: History of language model responses
        """

        SUCCESSFUL_RESPONSES = 'successful_responses'
        FAILED_RESPONSES = 'failed_responses'
        RESPONSES_HISTORY = 'responses_history'
