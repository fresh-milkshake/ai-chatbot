from abc import ABC, abstractmethod
from typing import Any, Optional, List


class DictionarySerializable(ABC):
    """
    Abstract class for converting objects to dictionaries.
    """

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key not in self.__annotations__:
                raise ValueError(f'Invalid argument: {key}')

            setattr(self, key, value)

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """
        Convert object to a dictionary.

        Returns:
            The object as a dictionary.
        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def force_from_dict(cls, data: dict[str, Any]) -> Any:
        """
        Convert a dictionary to a message object.

        Args:
            data: The dictionary to convert.

        Returns:
            True if the conversion was fully successful, False otherwise.
        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> Optional[Any]:
        """
        Convert a dictionary to a message object.

        Args:
            data: The dictionary to convert.
        """
        raise NotImplementedError()


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

    @classmethod
    def force_from_dict(cls, data: dict[str, Any]) -> Any:
        return Message(
            role=data.get('role', ''),
            content=data.get('content', '')
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Optional[Any]:
        if 'role' not in data or 'content' not in data:
            return None

        return Message(
            role=data['role'],
            content=data['content']
        )


class ConversationHistory(DictionarySerializable):
    """
    Class for containing history data and making operations on it.

    Attributes:
        messages: A list of messages
    """

    messages: list[Message]

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
        return [message.to_dict() for message in self.messages]

    @classmethod
    def force_from_dict(cls, data: list[dict]) -> Any:
        return ConversationHistory(messages=[Message.force_from_dict(message) for message in data])

    @classmethod
    def from_dict(cls, data: list[dict]) -> Optional[Any]:
        if not all(['role' in message and 'content' in message for message in data]):
            return None

        return ConversationHistory(messages=[Message.from_dict(message) for message in data])


class Model(DictionarySerializable):
    """
    Class for containing model data and making operations on it.

    Attributes:
        name: The name of the model.
        description: The description of the model.
        min_access_level: The minimum access level required to use the model.
        is_active: Whether the model is active or not.
    """

    name: str
    description: str = ''
    min_access_level: int
    is_active: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'min_access_level': self.min_access_level,
            'is_active': self.is_active
        }

    @classmethod
    def force_from_dict(cls, data: dict[str, Any]) -> Any:
        return Model(
            name=data.get('name', ''),
            description=data.get('description', ''),
            min_access_level=data.get('min_access_level', 0),
            is_active=data.get('is_active', True)
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Optional[Any]:
        if cls.__annotations__.keys() != data.keys():
            return None

        return Model(
            name=data['name'],
            description=data['description'],
            min_access_level=data['min_access_level'],
            is_active=data['is_active']
        )


class User(DictionarySerializable):
    """
    Class for containing user data and making operations on it.

    Attributes:
        first_name: The first name of the user.
        username: The username of the user.
        id: Telegram user id.
        language_code: Language code.
        is_premium: Whether the user is premium or not.
        is_bot: Whether the user is a bot or not.
        conversation: The conversation history of the user.
        model: The model the user is using.
    """

    first_name: str
    username: str
    id: str
    language_code: str

    is_premium: bool = False
    is_bot: bool = False

    conversation: ConversationHistory
    model: Model

    def to_dict(self) -> dict[str, Any]:
        return {
            'first_name': self.first_name,
            'username': self.username,
            'id': self.id,
            'language_code': self.language_code,
            'is_premium': self.is_premium,
            'is_bot': self.is_bot,
            'conversation': self.conversation.to_dict() if self.conversation else [],
            'model': self.model.to_dict() if self.model else {}
        }

    @classmethod
    def force_from_dict(cls, data: dict[str, Any]) -> Any:
        return User(
            first_name=data.get('first_name', ''),
            username=data.get('username', ''),
            id=data.get('id', ''),
            language_code=data.get('language_code', ''),
            is_premium=data.get('is_premium', False),
            is_bot=data.get('is_bot', False),
            conversation=ConversationHistory.force_from_dict(data.get('conversation', [])),
            model=Model.force_from_dict(data.get('model', {}))
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Optional[Any]:
        if cls.__annotations__.keys() != data.keys():
            return None

        return User(
            first_name=data['first_name'],
            username=data['username'],
            id=data['id'],
            language_code=data['language_code'],
            is_premium=data['is_premium'],
            is_bot=data['is_bot'],
            conversation=ConversationHistory.from_dict(data['conversation']),
            model=Model.from_dict(data['model'])
        )


if __name__ == '__main__':
    user = User(
        first_name='John',
        username='john',
        id='123',
        language_code='en',
        is_premium=True,
        is_bot=False,
        conversation=ConversationHistory(messages=[
            Message(role='user', content='Hello'),
            Message(role='assistant', content='Hi'),
            Message(role='system', content='How are you?')
        ]),
        model=Model(name='MyModel', description='This is a model', min_access_level=2, is_active=True)
    )

    assert type(user.to_dict()) == dict
    assert type(user.model.to_dict()) == dict
    assert type(user.conversation.messages[0].to_dict()) == dict

    assert type(user.first_name) == str
    assert type(user.username) == str
    assert type(user.id) == str

    assert user.to_dict() == User.from_dict(user.to_dict()).to_dict()
    assert user.to_dict() == User.force_from_dict(user.to_dict()).to_dict()
    assert User.from_dict(user.to_dict()).to_dict() == User.force_from_dict(user.to_dict()).to_dict()
