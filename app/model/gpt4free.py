from datetime import datetime

import g4f
from loguru import logger

from app.constants import DatabaseKeys
from app.constants.defaults import DEFAULT_MODEL
from app.database import Database
from app.dto import User
from app.model.abstraction import ChatProvider


class Gpt4FreeProviders(ChatProvider):
    """
    A class that encapsulates the OpenAI language model and provides an interface to use it.

    Attributes:

    """

    _instance = None

    error_responses_count: int
    success_responses_count: int
    total_responses_count: int

    def on_created(self):
        """
        Initialize the LanguageModel instance.
        """

        self.error_responses_count = 0
        self.success_responses_count = 0
        self.total_responses_count = 0

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

        error_message = None
        response = None
        answer = ''

        new_message = {'role': 'user', 'content': message}
        previous_conversation = user.get('conversation', [])
        messages = [*previous_conversation, new_message]

        try:
            logger.info(f'Calling Gpt4Free "{user.get(DatabaseKeys.User.CHOSEN_MODEL, "UNKNOWN")}" model')
            self.total_responses_count += 1

            # streamed completion
            response = g4f.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                stream=True,
            )

            for message in response:
                print(message, flush=True, end='')

            # normal response
            response = g4f.ChatCompletion.create(
                model=g4f.models.gpt_35_turbo,
                messages=messages,
            )  # alternative model setting

            choice = response.get('choices')[0]
            answer = choice.get('message').get('content')
            answer = answer.strip()
        except Exception as error:
            error_message = await handle_model_error(error)
        else:
            self.success_responses_count += 1
        finally:
            self.error_responses_count += 1

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

            return error_message + f'\n\nУровень стабильности: {self.stability_percentage:.2f}%'

        user['conversation'] = [
            *messages, {
                'role': 'assistant',
                'content': answer
            }
        ]

        Database().update_user_by_id(user)

        return answer

    @property
    def stability_percentage(self) -> float:
        if self.total_responses_count == 0:
            return 100.0

        return (self.success_responses_count / self.total_responses_count) * 100.0
