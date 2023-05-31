from datetime import datetime

import openai
from loguru import logger

from app.dto import User
from app.database.redis import RedisCache
from app.startup import OPENAI_TOKEN
from app.constants.strings import (
    MSG_ERROR_MODEL_API_ERROR,
    MSG_ERROR_MODEL_OPENAI_ERROR,
)
from app.constants.defaults import DEFAULT_MODEL
from app.constants import RedisKeys

logger.info('Defining OpenAI API key')
openai.api_key = OPENAI_TOKEN


class ExternalLanguageModel:
    """
    A class that encapsulates the OpenAI language model and provides an interface to use it.

    Attributes:
        responses_errors (list): A list of errors that occurred while using the OpenAI API.
        responses_successes_count (int): The number of successful API calls made.
        responses_total_count (int): The total number of API calls made.
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
            cls._instance = super(ExternalLanguageModel, cls).__new__(cls)
            cls.responses_errors = []
            cls.responses_successes_count = 0
            cls.responses_total_count = 0
        return cls._instance

    async def handle_model_error(self, error: openai.OpenAIError | Exception) -> None:
        """
        Handle an error that occurred while using the OpenAI API.

        Args:
            error: The OpenAI error to handle.
        """
        error_message = str(error)
        error_info = {'type': type(error).__name__, 'message': error_message}
        if isinstance(error, openai.OpenAIError):
            logger.error(f'OpenAI API error: {error_message}...', error_info=error_info)
            self.responses_errors.append(
                {'error': error_message, 'type': type(error).__name__, 'timestamp': datetime.now()})
            self.responses_total_count += 1
        elif isinstance(error, Exception):
            logger.error(f'Unknown error: {error_message}...', error_info=error_info)
            self.responses_errors.append(
                {'error': error_message, 'type': type(error).__name__, 'timestamp': datetime.now()})
            self.responses_total_count += 1

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
            logger.info(f'Calling OpenAI API "{user.get(RedisKeys.User.LOCAL_MODEL, "UNKNOWN")}" model')
            response = openai.ChatCompletion.create(model=user.get(RedisKeys.User.LOCAL_MODEL, DEFAULT_MODEL.name),
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
            self.responses_successes_count += 1

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
            self.responses_errors.append(
                {'error': error_message, 'user_id': user.get('id'), 'message': message, 'timestamp': datetime.now()})
            self.responses_total_count += 1

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

        if self.responses_total_count == 0:
            return 100.0

        return (self.responses_successes_count / self.responses_total_count) * 100.0
