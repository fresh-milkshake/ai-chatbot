from abc import ABC, abstractmethod

from loguru import logger
from telegram import Update


class Singleton(ABC):
    """
    Singleton class to inherit from.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            logger.debug(f'Creating new instance of {cls.__name__} with args: {[type(i) for i in args]} and kwargs: '
                         f'{[f"{k}={type(v)}" for k, v in kwargs.items()]}')
            cls._instance = super().__new__(cls)

        return cls._instance

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    def __repr__(self):
        return f'<{self.__class__.__name__} object at {hex(id(self))}>'


def get_user_string(update: Update) -> str:
    """
    Get a string representation of a user.

    Args:
        update: The update to get the user from.

    Returns:
        A string representation of the user.
    """
    return f"\"{update.effective_user.first_name} {update.effective_user.username}\" (ID{update.effective_user.id})"


def get_id_from_update(update: Update) -> int:
    """
    Get the user ID of a user.

    Args:
        update: The update to get the user from.

    Returns:
        The user ID of the user.
    """
    return update.effective_user.id


def get_user_name(update: Update) -> str:
    """
    Get the username of a user.

    Args:
        update: The update to get the user from.

    Returns:
        The username of the user.
    """
    return update.effective_user.first_name


if __name__ == '__main__':
    class ConcreteSingleton(Singleton):
        """
        Concrete singleton class.
        """

        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)


    testing_class = ConcreteSingleton

    s1 = testing_class(asd=123)
    s2 = testing_class()
    s3 = testing_class(a=1, b=2, c=3)

    assert s1 is s2 is s3
    assert type(s1) is type(s2) is type(s3) is testing_class
    assert s1.__dict__ == s2.__dict__ == s3.__dict__ == {'asd': 123, 'a': 1, 'b': 2, 'c': 3}
