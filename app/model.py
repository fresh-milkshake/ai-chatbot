import openai
from app.redis import RedisCache
from config import MODEL_NAME, OPENAI_API_KEY
from config.strings import (MSG_ERROR_MODEL_API_ERROR,
                            MSG_ERROR_MODEL_INVALID_REQUEST_ERROR,
                            MSG_ERROR_MODEL_OPENAI_ERROR)
from loguru import logger

logger.info('Defining OpenAI API key')
openai.api_key = OPENAI_API_KEY


class LanguageModel:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            logger.info('Creating new LanguageModel instance')
            cls._instance = super(LanguageModel, cls).__new__(cls)

        return cls._instance

    def create_answer(self, message: str, user: dict) -> str:
        """
        Create an answer to a message using the OpenAI API.

        Args:
            message: The message to answer.
            user: The user data dictionary from Redis.

        Returns:
            The answer to the message or an error message if the API call failed.
        """

        new_message = {'role': 'user', 'content': message}
        previous_conversation = user.get('conversation', [])
        messages = [*previous_conversation, new_message]

        try:
            response = openai.ChatCompletion.create(model=MODEL_NAME,
                                                    messages=messages)
            choice = response.get('choices')[0]
            answer = choice.get('message').get('content')
            answer = answer.strip()
        except openai.InvalidRequestError as e:
            logger.error(f'OpenAI API error: {e}')
            return MSG_ERROR_MODEL_INVALID_REQUEST_ERROR
        except openai.APIError as e:
            logger.error(f'OpenAI API error: {e}')
            return MSG_ERROR_MODEL_API_ERROR
        except openai.OpenAIError as e:
            logger.error(f'OpenAI API error: {e}')
            return MSG_ERROR_MODEL_OPENAI_ERROR

        user['conversation'] = [
            *messages, {
                'role': 'assistant',
                'content': answer
            }
        ]

        RedisCache().update_user(user['id'], user)

        return answer