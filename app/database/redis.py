import json
from typing import Dict, Any

import redis
from loguru import logger
from telegram import Update

from app.dto import User
from app.utils import get_user_string, Singleton

from app.startup import REDIS_PASSWORD, REDIS_HOST, REDIS_PORT, REDIS_DB_INDEX
from app.constants.defaults import DEFAULT_NEW_USER


def crud_request(func):
    """
    Decorator for class methods to handle Redis connection errors.

    Returns:
        The decorated function.

    See Also:
        :class:`app.database.redis.RedisCache` for example usage.
    """

    def error_handler(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except redis.exceptions.ConnectionError:
            logger.error('REDIS: Connection error')
            return None
        except Exception as e:
            logger.exception(f'REDIS: Unknown error: {e}')
            return None

    return error_handler


# TODO: test and look after this class after migration from custom Singleton implementation to Singleton inheritance from app.utils
class RedisCache(Singleton):
    """
    Singleton class for interacting with Redis Caching database.

    Attributes:
        redis_client: :class:`redis.Redis` instance for interacting with Redis database.

    See Also:
        :func:`app.database.redis.crud_request` for handling Redis connection errors.
        :class:`app.utils.Singleton` for singleton implementation.
    """

    # _instance = None

    # def __new__(cls):
    #     if cls._instance is None:
    #         logger.info('Creating new RedisCache instance')
    #         cls._instance = super(RedisCache, cls).__new__(cls)
    #         cls._instance.redis_client = redis.Redis(host=REDIS_HOST,
    #                                                  port=REDIS_PORT,
    #                                                  db=REDIS_DB_INDEX,
    #                                                  password=REDIS_PASSWORD)
    #     return cls._instance

    redis_client: redis.Redis = None

    def __init__(self):
        if self.redis_client is None:
            logger.info('Creating new RedisCache instance')
            self.redis_client = redis.Redis(host=REDIS_HOST,
                                            port=REDIS_PORT,
                                            db=REDIS_DB_INDEX,
                                            password=REDIS_PASSWORD)

    @crud_request
    def get_users(self) -> Dict[str, dict]:
        """
        Get all user data from the Redis cache.

        Returns:
            A dictionary mapping user IDs to user data dictionaries.
        """
        logger.debug('REDIS: Getting users')
        users = {}
        for key in self.redis_client.scan_iter(match="user:*"):
            user_id = key.decode().split(':')[1]
            user_data = self.redis_client.hgetall(key)
            users[user_id] = {
                k.decode(): json.loads(v.decode())
                for k, v in user_data.items()
            }
        return users

    @crud_request
    def update_users(self, users: Dict[str, dict]) -> bool:
        """
        Update all user data in the Redis cache.

        Args:
            users: A dictionary mapping user IDs to user data dictionaries.

        Returns:
            A boolean indicating if the update was successful.
        """
        logger.debug('REDIS: Updating users')
        try:
            with self.redis_client.pipeline() as pipe:
                for user_id, user_data in users.items():
                    pipe.hmset(
                        f"user:{user_id}",
                        {k: json.dumps(v)
                         for k, v in user_data.items()})
                pipe.execute()
            return True
        except Exception as e:
            logger.error(f"REDIS: Failed to update users: {e}")
            return False

    @crud_request
    def update_user(self, user_id: int, user_data: dict) -> bool:
        """
        Update user data for a given user ID.

        Args:
            user_id: The ID of the user to update.
            user_data: The user data dictionary to save.

        Returns:
            A boolean indicating if the update was successful.
        """
        logger.debug(f"REDIS: Updating user with ID {user_id}")
        try:
            self.redis_client.hmset(
                f"user:{user_id}",
                {k: json.dumps(v)
                 for k, v in user_data.items()})
            return True
        except Exception as e:
            logger.error(f"REDIS: Failed to update user {user_id}: {e}")
            return False

    @crud_request
    def _get_user_by_id(self, user_id: int) -> dict:
        """
        Get user data for a given user ID.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            A dictionary containing the user data for the specified user ID.
        """
        user_data_raw = self.redis_client.hgetall(f"user:{user_id}")
        if not user_data_raw:
            return {}
        return {
            k.decode(): json.loads(v.decode())
            for k, v in user_data_raw.items()
        }

    @crud_request
    def get_user(self, user_id: int) -> dict:
        """
        Get user data for a given user ID.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            A dictionary containing the user data for the specified user ID.
        """
        logger.debug(f"REDIS: Getting user with ID {user_id}")
        user_data = self._get_user_by_id(user_id)
        if not user_data:
            logger.warning(f"REDIS: User with ID {user_id} not found")
        return user_data

    @crud_request
    def get_user_by_update(self, update: Update) -> dict:
        """
        Get user data for a given update object.

        Args:
            update: An update object containing user information.

        Returns:
            A dictionary containing the user data for the specified user ID.
        """
        logger.debug(f"REDIS: Getting user with ID {update.effective_user.id}")
        user_id = update.effective_user.id
        user_data = self._get_user_by_id(user_id)
        if not user_data:
            self.create_user_from_update(update)
            user_data = self._get_user_by_id(user_id)
        return user_data

    @crud_request
    def delete_user(self, user_id: int) -> bool:
        """
        Delete user data for a given user ID.

        Args:
            user_id: The ID of the user to delete.

        Returns:
            A boolean indicating if the deletion was successful.
        """
        logger.debug(f"REDIS: Deleting user with ID {user_id}")
        try:
            self.redis_client.delete(f"user:{user_id}")
            return True
        except Exception as e:
            logger.error(f"REDIS: Failed to delete user {user_id}: {e}")
            return False

    @crud_request
    def create_user_from_update(self, update: Update) -> bool:
        """
        Create a new user from an update object.

        Args:
            update: An update object containing user information.

        Returns:
            A boolean indicating if the user creation was successful.
        """
        logger.info(f'REDIS: Creating new user {get_user_string(update)}')

        user_id = update.effective_user.id
        user_data = {**update.effective_user.to_dict(), **DEFAULT_NEW_USER}
        return self.update_user(user_id, user_data)


class RedisCacheInterface:
    """
    A Singleton class that provides a Redis cache interface for User objects.
    This class is responsible for managing users in the Redis cache and
    performing CRUD operations with User objects.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            logger.info('Creating new RedisCacheWithClasses instance')
            cls._instance = super(RedisCacheInterface, cls).__new__(cls)
            cls._instance.redis_client = redis.Redis(host=REDIS_HOST,
                                                     port=REDIS_PORT,
                                                     db=REDIS_DB_INDEX,
                                                     password=REDIS_PASSWORD)
        return cls._instance

    def get_users(self) -> Dict[str, User]:
        """
        Retrieves all User objects from the Redis cache.

        Returns:
            A dictionary where the keys are user IDs and the values are User objects.
        """

        logger.debug('REDIS: Getting users')
        users = {}
        for key in self.redis_client.scan_iter(match="user:*"):
            user_id = key.decode().split(':')[1]
            user_data = self.redis_client.hgetall(key)
            users[user_id] = User.from_dict(
                {
                    k.decode(): json.loads(v.decode())
                    for k, v in user_data.items()
                }
            )
        return users

    def update_users(self, users: Dict[str, User]) -> bool:
        """
        Updates multiple User objects in the Redis cache.

        Args:
            users: A dictionary where the keys are user IDs and the values are User objects.

        Returns:
            A boolean indicating if the update was successful.
        """

        logger.debug('REDIS: Updating users')
        try:
            with self.redis_client.pipeline() as pipe:
                for user_id, user in users.items():
                    pipe.hmset(
                        f"user:{user_id}",
                        {k: json.dumps(v)
                         for k, v in user.to_dict().items()})
                pipe.execute()
            return True
        except Exception as e:
            logger.error(f"REDIS: Failed to update users: {e}")
            return False

    def update_user(self, user_id: int, user: User) -> bool:
        """
        Updates a single User object in the Redis cache.

        Args:
            user_id: The ID of the user to update.
            user: The User object to update.

        Returns:
            A boolean indicating if the update was successful.
        """

        logger.debug(f"REDIS: Updating user with ID {user_id}")
        try:
            self.redis_client.hmset(
                f"user:{user_id}",
                {k: json.dumps(v)
                 for k, v in user.to_dict().items()})
            return True
        except Exception as e:
            logger.error(f"REDIS: Failed to update user {user_id}: {e}")
            return False

    def _get_user_by_id(self, user_id: int) -> Any | None:
        """
        Retrieves a User object by user ID from the Redis cache.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            The User object if it exists, otherwise None.
        """

        user_data_raw = self.redis_client.hgetall(f"user:{user_id}")
        if not user_data_raw:
            return None
        return User.from_dict(
            {
                k.decode(): json.loads(v.decode())
                for k, v in user_data_raw.items()
            }
        )

    def get_user(self, user_id: int) -> User:
        """
        Retrieves a User object by user ID from the Redis cache.
        Logs a warning if the user is not found.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            The User object if it exists, otherwise None.
        """

        logger.debug(f"REDIS: Getting user with ID {user_id}")
        user = self._get_user_by_id(user_id)
        if user is None:
            logger.warning(f"REDIS: User with ID {user_id} not found")
        return user

    def get_user_by_update(self, update: Update) -> User:
        """
        Retrieves a User object from the Redis cache using an Update object.
        Creates a new user in the cache if it doesn't exist.

        Args:
            update: The Update object containing user information.

        Returns:
            The User object corresponding to the user in the Update object.
        """

        logger.debug(f"REDIS: Getting user with ID {update.effective_user.id}")
        user_id = update.effective_user.id
        user = self._get_user_by_id(user_id)
        if user is None:
            self.create_user_from_update(update)
            user = self._get_user_by_id(user_id)
        return user

    def delete_user(self, user_id: int) -> bool:
        """
        Deletes a User object by user ID from the Redis cache.

        Args:
            user_id: The ID of the user to delete.

        Returns:
            A boolean indicating if the deletion was successful.
        """

        logger.debug(f"REDIS: Deleting user with ID {user_id}")
        try:
            self.redis_client.delete(f"user:{user_id}")
            return True
        except Exception as e:
            logger.error(f"REDIS: Failed to delete user {user_id}: {e}")
            return False

    def create_user_from_update(self, update: Update) -> bool:
        """
        Creates a new User object in the Redis cache using an Update object.

        Args:
            update: The Update object containing user information.

        Returns:
            A boolean indicating if the user creation was successful.
        """

        logger.info(f'REDIS: Creating new user {get_user_string(update)}')

        user_id = update.effective_user.id
        user_data = {**update.effective_user.to_dict(), **DEFAULT_NEW_USER}
        user = User.force_from_dict(user_data)
        return self.update_user(user_id, user)
