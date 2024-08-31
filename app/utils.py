from typing import final

from loguru import logger
from telegram import Update


class Singleton:
    """
    Singleton class to inherit from.
    """

    _instance = None

    @final
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            logger.info(f'Creating instance of {cls.__name__}')
            logger.debug(f'Creating new instance of {cls.__name__} with args: {[type(i) for i in args]} and kwargs: '
                         f'{[f"{k}={type(v)}" for k, v in kwargs.items()]}')
            cls._instance = super().__new__(cls)
            cls._instance.on_created(*args, **kwargs)

        cls._instance.on_acquire(*args, **kwargs)
        return cls._instance

    def on_created(self, *args, **kwargs):
        """
        Method called after the singleton object is created.

        Args:
            *args: The arguments passed to the constructor.
            **kwargs: The keyword arguments passed to the constructor.
        """
        pass

    def on_acquire(self, *args, **kwargs):
        """
        Method called after the singleton object is acquired from the
        singleton class.

        Args:
            *args: The arguments passed to the constructor.
            **kwargs: The keyword arguments passed to the constructor.
        """
        pass

    def __repr__(self):
        return f'<{self.__class__.__name__} object at {hex(id(self))} [singleton object is {hex(id(self.__class__._instance))}]>'



def get_user_string(update: Update) -> str:
    """
    Get a string representation of a user.
    
    "$first_name$ $username$ $user_id$"

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

        created: bool

        def on_acquire(self, *args, **kwargs):
            self.__dict__.update(kwargs)

        def on_created(self, *args, **kwargs):
            self.created = True


    testing_class = ConcreteSingleton

    assert testing_class().created is True

    s1 = testing_class(asd=123)
    s2 = testing_class()
    s3 = testing_class(a=1, b=2, c=3)

    assert s1 is s2 is s3
    assert type(s1) is type(s2) is type(s3) is testing_class
    assert s1.__dict__ == s2.__dict__ == s3.__dict__ == {'asd': 123, 'a': 1, 'b': 2, 'c': 3, 'created': True}
