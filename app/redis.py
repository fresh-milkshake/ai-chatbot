import json
from typing import Dict

import redis
from loguru import logger
from telegram import Update

from config import REDIS_PASSWORD, REDIS_DB_INDEX, REDIS_PORT, REDIS_HOST, DEFAULT_NEW_USER
from utils.strings import get_user_string


class RedisCache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            logger.info('Creating new RedisCache instance')
            cls._instance = super(RedisCache, cls).__new__(cls)
            cls._instance.redis_client = redis.Redis(host=REDIS_HOST,
                                                     port=REDIS_PORT,
                                                     db=REDIS_DB_INDEX,
                                                     password=REDIS_PASSWORD)
        return cls._instance

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
