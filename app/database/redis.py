import json
from dataclasses import dataclass
from typing import Dict, Any, TypeVar, Generic

import redis
from loguru import logger
from telegram import Update

from app.constants.defaults import DEFAULT_NEW_USER
from app.startup import REDIS_PASSWORD, REDIS_HOST, REDIS_PORT, REDIS_DB_INDEX
from app.utils import get_user_string
from .abstraction import StorageProvider


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
            logger.error(f'REDIS: Unknown error: {e}')
            return None

    return error_handler


T = TypeVar('T')


@dataclass
class RedisResponse(Generic[T]):
    """
    Dataclass for Redis responses.

    Attributes:
        success: Whether the request was successful.
        data: The data returned by the request.
    """

    success: bool
    data: T


def wrap_response(response: Any) -> RedisResponse[Any]:
    """
    Handle a Redis response by wrapping its data in a :class:`app.database.redis.RedisResponse` instance.


    Args:
        response: The response from a Redis request.

    Returns:
        A :class:`app.database.redis.RedisResponse` instance.
    """
    # TODO: figure out how to make error pass to `success`
    return RedisResponse(success=True, data=response)


# TODO: rewrite whole class to use async and newer version features of redis-py
class RedisCache(StorageProvider):
    """
    Singleton class for interacting with a Redis Caching database.

    Attributes:
        redis_client: :class:`redis.Redis` instance for interacting with a Redis database.

    See Also:
        :func:`app.database.redis.crud_request` for handling Redis connection errors.
        :class:`app.utils.Singleton` for singleton implementation.
    """

    redis_client: redis.Redis = None

    def on_created(self):
        logger.debug(
            f'Connecting to Redis at {REDIS_HOST}:{REDIS_PORT} with password {REDIS_PASSWORD[:3]}...{REDIS_PASSWORD[-3:]}')
        self.redis_client = redis.Redis(host=REDIS_HOST,
                                        port=REDIS_PORT,
                                        db=REDIS_DB_INDEX,
                                        password=REDIS_PASSWORD)

    @crud_request
    def get_users(self) -> RedisResponse[Dict[str, Dict]]:
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
        return wrap_response(users)

    @crud_request
    def update_users(self, users: Dict[str, dict]) -> RedisResponse[bool]:
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
            return wrap_response(True)
        except Exception as e:
            logger.error(f"REDIS: Failed to update users: {e}")
            return wrap_response(False)

    @crud_request
    def update_user_by_id(self, user_id: int, user_data: dict) -> RedisResponse[bool]:
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
            return wrap_response(True)
        except Exception as e:
            logger.error(f"REDIS: Failed to update user {user_id}: {e}")
            return wrap_response(False)

    @crud_request
    def update_user(self, user_data: dict) -> RedisResponse[bool]:
        """
        Update user data for a given user.

        Args:
            user_data: The user data dictionary to save.

        Returns:
            A boolean indicating if the update was successful.
        """
        user_id = user_data.get('id')
        if not user_id:
            logger.error(f"REDIS: Failed to update user: user ID not found")
            return wrap_response(False)

        logger.debug(f"REDIS: Updating user with ID {user_id}")
        try:
            self.redis_client.hmset(
                f"user:{user_id}",
                {k: json.dumps(v)
                 for k, v in user_data.items()})
            return wrap_response(True)
        except Exception as e:
            logger.error(f"REDIS: Failed to update user {user_id}: {e}")
            return wrap_response(False)

    @crud_request
    def _get_user_by_id(self, user_id: int) -> RedisResponse[dict]:
        """
        Get user data for a given user ID.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            A dictionary containing the user data for the specified user ID.
        """
        user_data_raw = self.redis_client.hgetall(f"user:{user_id}")
        if not user_data_raw:
            return wrap_response({})
        return wrap_response(
            {
                k.decode(): json.loads(v.decode())
                for k, v in user_data_raw.items()
            }
        )

    @crud_request
    def get_user(self, user_id: int) -> RedisResponse[dict]:
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
        return wrap_response(user_data)

    @crud_request
    def get_user_by_update(self, update: Update) -> RedisResponse[dict]:
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
        return wrap_response(user_data)

    @crud_request
    def delete_user(self, user_id: int) -> RedisResponse[bool]:
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
            return wrap_response(True)
        except Exception as e:
            logger.error(f"REDIS: Failed to delete user {user_id}: {e}")
            return wrap_response(False)

    @crud_request
    def create_user_from_update(self, update: Update) -> RedisResponse[bool]:
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
        return self.update_user_by_id(user_id, user_data)
