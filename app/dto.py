from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional, List


class DictionarySerializable(ABC):
    """
    Abstract class for converting objects to dictionaries.
    """

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """
        Convert object to a dictionary.

        Returns:
            The object as a dictionary.
        """
        pass

    @staticmethod
    @abstractmethod
    def force_from_dict(data: dict[str, Any]) -> Any:
        """
        Convert a dictionary to a message object.

        Args:
            data: The dictionary to convert.

        Returns:
            True if the conversion was fully successful, False otherwise.
        """
        pass

    @staticmethod
    @abstractmethod
    def from_dict(data: dict[str, Any]) -> Optional[Any]:
        """
        Convert a dictionary to a message object.

        Args:
            data: The dictionary to convert.
        """
        pass


@dataclass
class Message(DictionarySerializable):
    """
    Class for containing message data.

    Attributes:
        role: The role of the message (user, assistant or system).
        content: The text content of the message.
    """

    role: str
    content: str

    def to_dict(self) -> dict[str, str]:
        return {
            'role': self.role,
            'content': self.content
        }

    @staticmethod
    def force_from_dict(data: dict[str, Any]) -> Any:
        return Message(
            data.get('role', ''),
            data.get('content', '')
        )

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Optional[Any]:
        if 'role' not in data or 'content' not in data:
            return None

        return Message(
            data['role'],
            data['content']
        )


class ConversationHistory(DictionarySerializable):
    """
    Class for containing history data and making operations on it.

    Attributes:
        messages: A list of messages
    """

    def __init__(self, messages: Optional[List[Message]] = None):
        """
        Initialize the History class.

        Args:
            messages: An already existing list of messages and their data.
        """

        if messages is None:
            messages = []

        self.messages = messages

    def add_message(self, message: Message) -> None:
        """
        Add a message to the history.

        Args:
            message: The message to add.
        """

        self.messages.append(message)

    def remove_message(self, message: Message) -> None:
        """
        Remove a message from the history.

        Args:
            message: The message to remove.
        """

        self.messages.remove(message)

    def pop_message(self, index: Optional[int] = 0) -> None:
        """
        Remove a message from the history.

        Args:
            index: The index of the message to remove.
        """

        self.messages.pop(index)

    def to_dict(self) -> list[Any]:
        """
        Convert the history to a dictionary.

        Returns:
            The messages history as a dictionary.
        """

        return [message.to_dict() for message in self.messages]

    @staticmethod
    def force_from_dict(data: dict[str, Any]) -> Any:
        return ConversationHistory([Message.force_from_dict(message) for message in data.get('messages', [])])

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Optional[Any]:
        if 'messages' not in data:
            return None

        return ConversationHistory([Message.from_dict(message) for message in data['messages']])


class User(DictionarySerializable):
    """
    Class for containing user data and making operations on it.
    """

    def __init__(self, user_data: dict, conversation: Optional[ConversationHistory | list] = None):
        """
        Initialize the User class.

        Args:
            user_data: An already existing dictionary of user data.
        """

        self.first_name = user_data.get('first_name', '')
        self.username = user_data.get('username', '')
        self.id = user_data.get('id', '')
        self.language_code = user_data.get('language_code', '')

        self.is_premium = user_data.get('is_premium', False)
        self.is_bot = user_data.get('is_bot', False)

        self.conversation = ConversationHistory(conversation)

    def to_dict(self) -> dict[str, Any]:
        return {
            'first_name': self.first_name,
            'username': self.username,
            'id': self.id,
            'language_code': self.language_code,
            'conversation': self.conversation.to_dict(),
            'is_premium': self.is_premium,
            'is_bot': self.is_bot
        }

    @staticmethod
    def force_from_dict(data: dict[str, Any]) -> Any:
        return User(
            data.get('user_data', {}),
            data.get('conversation', [])
        )

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Optional[Any]:
        if 'user_data' not in data or 'conversation' not in data:
            return None

        return User(
            data['user_data'],
            data['conversation']
        )
