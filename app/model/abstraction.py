from dataclasses import dataclass
from typing import Generic, TypeVar, Dict
from abc import ABC, abstractmethod

from telegram import Update

from app.dto import User
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


class ChatProvider(Singleton, ABC):
    """
    Singleton class for interacting with an X database.

    See Also:
        :class:`app.utils.Singleton` for singleton implementation.
    """

    def on_created(self):
        raise NotImplementedError

    @abstractmethod
    async def create_answer(self, message: str, user: dict | User) -> str:
        """
        Create an answer to a message using the OpenAI API.

        Args:
            message: The message to answer.
            user: The user data dictionary from Redis.

        Returns:
            The answer to the message or an error message if the API call failed.
        """
        raise NotImplementedError

    @abstractmethod
    def stability_percentage(self) -> float:
        """
        Calculate the percentage of stable operation.

        Returns:
            The percentage of stable operations as a float between 0.0 and 100.0.
        """
        raise NotImplementedError
