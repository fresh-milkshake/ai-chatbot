from dataclasses import dataclass
from typing import Generic, TypeVar, Dict
from abc import ABC, abstractmethod

from telegram import Update

from app.utils import Singleton

T = TypeVar("T")


@dataclass
class Response(Generic[T]):
    """
    A generic dataclass representing responses from database operations.

    Attributes:
        success (bool): Indicates whether the database operation was successful.
        data (T): The data returned by the operation. The type varies based on the operation.
    """

    success: bool
    data: T


class StorageProvider(Singleton, ABC):
    """
    An abstract base class defining the interface for database storage providers.

    This class implements the Singleton pattern to ensure only one instance exists.
    Subclasses should implement all abstract methods to provide specific database functionality.

    See Also:
        :class:`app.utils.Singleton` for details on the Singleton implementation.
    """

    def on_created(self):
        """
        Initialize the storage provider when it's first created.

        This method should be overridden by subclasses to perform any necessary setup.
        """
        raise NotImplementedError

    @abstractmethod
    def get_data(self):
        """
        Retrieve all data from the storage.

        This method should be implemented by subclasses to fetch all stored data.
        """
        raise NotImplementedError

    @abstractmethod
    def get_users(self) -> Response[Dict[str, Dict]]:
        """
        Retrieve all user data from the storage.

        Returns:
            Response[Dict[str, Dict]]: A Response object containing a dictionary mapping
            user IDs (str) to user data dictionaries.
        """
        raise NotImplementedError

    @abstractmethod
    def update_users(self, users: Dict[str, dict]) -> Response[bool]:
        """
        Update multiple users' data in the storage.

        Args:
            users (Dict[str, dict]): A dictionary mapping user IDs to user data dictionaries.

        Returns:
            Response[bool]: A Response object indicating whether the update was successful.
        """
        raise NotImplementedError

    @abstractmethod
    def update_user_by_id(self, user_id: int, user_data: dict) -> Response[bool]:
        """
        Update a specific user's data in the storage.

        Args:
            user_id (int): The ID of the user to update.
            user_data (dict): The updated user data dictionary.

        Returns:
            Response[bool]: A Response object indicating whether the update was successful.
        """
        raise NotImplementedError

    @abstractmethod
    def update_user(self, user_data: dict) -> Response[bool]:
        """
        Update a user's data in the storage.

        Args:
            user_data (dict): The user data dictionary to update.

        Returns:
            Response[bool]: A Response object indicating whether the update was successful.
        """
        raise NotImplementedError

    @abstractmethod
    def _get_user_by_id(self, user_id: int) -> Response[dict]:
        """
        Internal method to retrieve a user's data by their ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            Response[dict]: A Response object containing the user's data dictionary.
        """
        raise NotImplementedError

    @abstractmethod
    def get_user(self, user_id: int) -> Response[dict]:
        """
        Retrieve a user's data by their ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            Response[dict]: A Response object containing the user's data dictionary.
        """
        raise NotImplementedError

    @abstractmethod
    def get_user_by_update(self, update: Update) -> Response[dict]:
        """
        Retrieve a user's data from a Telegram Update object.

        Args:
            update (Update): A Telegram Update object containing user information.

        Returns:
            Response[dict]: A Response object containing the user's data dictionary.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_user(self, user_id: int) -> Response[bool]:
        """
        Delete a user's data from the storage.

        Args:
            user_id (int): The ID of the user to delete.

        Returns:
            Response[bool]: A Response object indicating whether the deletion was successful.
        """
        raise NotImplementedError

    @abstractmethod
    def create_user_from_update(self, update: Update) -> Response[bool]:
        """
        Create a new user entry from a Telegram Update object.

        Args:
            update (Update): A Telegram Update object containing user information.

        Returns:
            Response[bool]: A Response object indicating whether the user creation was successful.
        """
        raise NotImplementedError
