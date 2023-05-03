from datetime import datetime

import openai
from loguru import logger

from app.dto import User
from app.redis import RedisCache
from config import GLOBAL_DEFAULT_MODEL, OPENAI_API_KEY, REDIS_USER_LOCAL_MODEL
from config.strings import (
    MSG_ERROR_MODEL_API_ERROR,
    MSG_ERROR_MODEL_OPENAI_ERROR,
)

logger.info('Defining OpenAI API key')
openai.api_key = OPENAI_API_KEY


class LanguageModel:
    """
    A class that encapsulates the OpenAI language model and provides an interface to use it.

    Attributes:
        errors (list): A list of errors that occurred while using the OpenAI API.
        success_count (int): The number of successful API calls made.
        total_count (int): The total number of API calls made.
    """

    _instance = None

    def __new__(cls):
        """
        Create a new instance of the LanguageModel class if one does not exist.

        Returns:
            The LanguageModel instance.
        """
        if cls._instance is None:
            logger.info('Creating new LanguageModel instance')
            cls._instance = super(LanguageModel, cls).__new__(cls)
            cls.errors = []
            cls.success_count = 0
            cls.total_count = 0
        return cls._instance

    async def handle_model_error(self, error: openai.OpenAIError) -> None:
        """
        Handle an error that occurred while using the OpenAI API.

        Args:
            error: The OpenAI error to handle.
        """
        error_message = str(error)
        error_info = {'type': type(error).__name__, 'message': error_message}
        logger.error(f'OpenAI API error: {error_message}...', error_info=error_info)
        self.errors.append({'error': error_message, 'type': type(error).__name__, 'timestamp': datetime.now()})
        self.total_count += 1

    async def create_answer(self, message: str, user: dict | User) -> str:
        """
        Create an answer to a message using the OpenAI API.

        Args:
            message: The message to answer.
            user: The user data dictionary from Redis.

        Returns:
            The answer to the message or an error message if the API call failed.
        """

        if isinstance(user, User):
            user = user.to_dict()

        new_message = {'role': 'user', 'content': message}
        previous_conversation = user.get('conversation', [])
        messages = [*previous_conversation, new_message]
        response = None
        answer = ''

        try:
            logger.info(f'Calling OpenAI API "{user.get(REDIS_USER_LOCAL_MODEL, "UNKNOW")}" model')
            response = openai.ChatCompletion.create(model=user.get(REDIS_USER_LOCAL_MODEL, GLOBAL_DEFAULT_MODEL.name),
                                                    messages=messages)
            choice = response.get('choices')[0]
            answer = choice.get('message').get('content')
            answer = answer.strip()

        except openai.APIError as e:
            error_message = MSG_ERROR_MODEL_API_ERROR
            await self.handle_model_error(e)

        except openai.OpenAIError as e:
            await self.handle_model_error(e)
            error_message = MSG_ERROR_MODEL_OPENAI_ERROR

        except Exception as e:
            error_message = MSG_ERROR_MODEL_OPENAI_ERROR
            await self.handle_model_error(e)

        else:
            error_message = None
            self.success_count += 1

        if error_message is not None:
            error_info = {
                'user_id': user.get('id'),
                'message': message,
                'previous_conversation': previous_conversation,
                'response': response.to_dict() if response else None,
                'error_message': error_message,
                'timestamp': datetime.now()
            }
            logger.error(error_message, error_info=error_info)
            self.errors.append(
                {'error': error_message, 'user_id': user.get('id'), 'message': message, 'timestamp': datetime.now()})
            self.total_count += 1

            return error_message + f'\n\nУровень стабильности: {self.stability_percentage:.2f}%'

        user['conversation'] = [
            *messages, {
                'role': 'assistant',
                'content': answer
            }
        ]

        RedisCache().update_user(user['id'], user)

        return answer

    @property
    def stability_percentage(self) -> float:
        """
        Calculate the percentage of stable operation.

        Returns:
            The percentage of stable operation, as a float between 0.0 and 100.0.
        """

        if self.total_count == 0:
            return 100.0

        return 100.0 * self.success_count / self.total_count
