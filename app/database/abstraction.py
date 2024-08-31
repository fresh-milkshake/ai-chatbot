from dataclasses import dataclass
from typing import Generic, TypeVar, Dict
from abc import ABC, abstractmethod

from telegram import Update

from app.utils import Singleton

T = TypeVar('T')


@dataclass
class Response(Generic[T]):
    """
    Dataclass for responses from databases.

    Attributes:
        success: Whether the request was successful.
        data: The data returned by the request.
    """

    success: bool
    data: T


class StorageProvider(Singleton, ABC):
    """
    Singleton class for interacting with an X database.

    See Also:
        :class:`app.utils.Singleton` for singleton implementation.
    """

    def on_created(self):
        raise NotImplementedError

    @abstractmethod
    def get_data(self):
        raise NotImplementedError

    @abstractmethod
    def get_users(self) -> Response[Dict[str, Dict]]:
        """
        Get all user data from the Redis cache.

        Returns:
            A dictionary mapping user IDs to user data dictionaries.
        """
        raise NotImplementedError

    @abstractmethod
    def update_users(self, users: Dict[str, dict]) -> Response[bool]:
        """
        Update all user data in the Redis cache.

        Args:
            users: A dictionary mapping user IDs to user data dictionaries.

        Returns:
            A boolean indicating if the update was successful.
        """
        raise NotImplementedError

    @abstractmethod
    def update_user_by_id(self, user_id: int, user_data: dict) -> Response[bool]:
        """
        Update user data for a given user ID.

        Args:
            user_id: The ID of the user to update.
            user_data: The user data dictionary to save.

        Returns:
            A boolean indicating if the update was successful.
        """
        raise NotImplementedError

    @abstractmethod
    def update_user(self, user_data: dict) -> Response[bool]:
        """
        Update user data for a given user.

        Args:
            user_data: The user data dictionary to save.

        Returns:
            A boolean indicating if the update was successful.
        """
        raise NotImplementedError

    @abstractmethod
    def _get_user_by_id(self, user_id: int) -> Response[dict]:
        """
        Get user data for a given user ID.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            A dictionary containing the user data for the specified user ID.
        """
        raise NotImplementedError

    @abstractmethod
    def get_user(self, user_id: int) -> Response[dict]:
        """
        Get user data for a given user ID.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            A dictionary containing the user data for the specified user ID.
        """
        raise NotImplementedError

    @abstractmethod
    def get_user_by_update(self, update: Update) -> Response[dict]:
        """
        Get user data for a given update object.

        Args:
            update: An update object containing user information.

        Returns:
            A dictionary containing the user data for the specified user ID.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_user(self, user_id: int) -> Response[bool]:
        """
        Delete user data for a given user ID.

        Args:
            user_id: The ID of the user to delete.

        Returns:
            A boolean indicating if the deletion was successful.
        """
        raise NotImplementedError

    @abstractmethod
    def create_user_from_update(self, update: Update) -> Response[bool]:
        """
        Create a new user from an update object.

        Args:
            update: An update object containing user information.

        Returns:
            A boolean indicating if the user creation was successful.
        """
        raise NotImplementedError
