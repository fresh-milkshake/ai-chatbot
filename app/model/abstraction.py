from typing import AsyncGenerator
from abc import ABC, abstractmethod


from app.dto import User
from app.utils import Singleton


StreamedReadableAnswer = AsyncGenerator[str, None]
ReadableAnswer = str


class ChatProvider(Singleton, ABC):
    """
    Abstract base class for chat providers, implementing the Singleton pattern.

    This class defines the interface for chat providers that can create and stream answers
    to user messages. It ensures only one instance of each provider is created.

    Attributes:
        None

    See Also:
        :class:`app.utils.Singleton` for the singleton implementation details.
    """

    @abstractmethod
    def on_created(self):
        """
        Initialize the chat provider instance.

        This method is called once when the singleton instance is created.
        Subclasses should implement this method to perform any necessary setup.
        """
        raise NotImplementedError

    @abstractmethod
    async def create_answer(self, message: str, user: dict | User) -> ReadableAnswer:
        """
        Create a complete answer to a user's message.

        This method generates a full response to the given message, considering the user's
        context and conversation history.

        Args:
            message (str): The user's input message to be answered.
            user (dict | User): The user's data, either as a dictionary or User object.

        Returns:
            ReadableAnswer: A string containing the complete answer to the user's message.

        Raises:
            NotImplementedError: If not implemented by a subclass.
        """
        raise NotImplementedError

    @abstractmethod
    async def stream_answer(
        self, message: str, user: dict | User
    ) -> StreamedReadableAnswer:
        """
        Stream an answer to a user's message.

        This method generates and yields parts of the answer as they become available,
        allowing for real-time streaming of the response.

        Args:
            message (str): The user's input message to be answered.
            user (dict | User): The user's data, either as a dictionary or User object.

        Yields:
            str: Portions of the answer as they are generated.

        Raises:
            NotImplementedError: If not implemented by a subclass.
        """
        raise NotImplementedError

    @abstractmethod
    def stability_percentage(self) -> float:
        """
        Calculate and return the stability percentage of the chat provider.

        This method should compute a measure of how stable the chat provider's
        operations have been, based on factors such as successful responses,
        error rates, or other relevant metrics.

        Returns:
            float: The stability percentage, ranging from 0.0 to 100.0.

        Raises:
            NotImplementedError: If not implemented by a subclass.
        """
        raise NotImplementedError
