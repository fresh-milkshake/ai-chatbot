from datetime import datetime

import openai
import tiktoken
from loguru import logger

from app.constants import DatabaseKeys
from app.constants.defaults import DEFAULT_MODEL
from app.constants.strings import (
    MSG_ERROR_MODEL_API_ERROR,
    MSG_ERROR_MODEL_OPENAI_ERROR,
)
from app.database import Database
from app.dto import User
from app.model.abstraction import ChatProvider
from app.startup import OPENAI_TOKEN

logger.info("Defining OpenAI API key")
openai.api_key = OPENAI_TOKEN
Tokenizer = tiktoken.get_encoding("cl100k_base")


def get_tokens_count(text: str) -> int:
    """
    Get the number of tokens in a text.

    Args:
        text: The text to get the number of tokens in.

    Returns:
        The number of tokens in the text.
    """
    return len(Tokenizer.encode(text))


async def calculate_conversion_tokens(user: dict | User) -> int:
    """
    Calculate the number of tokens in a user's conversation.

    Args:
        user: The user data dictionary from Redis.

    Returns:
        The number of tokens in the user's conversation.
    """

    if isinstance(user, User):
        user = user.to_dict()

    conversation = user.get("conversation", [])
    tokens = 0

    for message in conversation:
        tokens += get_tokens_count(message.get("content"))

    return tokens


async def handle_model_error(error: openai.OpenAIError | Exception) -> str:
    """
    Handle an error that occurred while using the OpenAI API.

    Args:
        error: The OpenAI error to handle.
    """
    error_message = str(error)
    error_info = {
        "error": error_message,
        "type": type(error).__name__,
        "timestamp": datetime.now(),
    }
    logger.error(error_info)

    match type(error):
        case openai.error.APIError:
            return MSG_ERROR_MODEL_API_ERROR.format(error_message)
        case openai.error.AuthenticationError:
            return MSG_ERROR_MODEL_API_ERROR.format(error_message)
        case openai.error.InvalidRequestError:
            return MSG_ERROR_MODEL_API_ERROR.format(error_message)
        case openai.error.RateLimitError:
            return MSG_ERROR_MODEL_API_ERROR.format(error_message)
        case openai.error.PermissionError:
            return MSG_ERROR_MODEL_API_ERROR.format(error_message)
        case openai.error.OpenAIError:
            return MSG_ERROR_MODEL_OPENAI_ERROR.format(error_message)
        case _:
            return MSG_ERROR_MODEL_OPENAI_ERROR.format(error_message)


class OpenAIModels(ChatProvider):
    """
    A class that encapsulates the OpenAI language models and provides an interface to use it.

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
        answer = ""

        new_message = {"role": "user", "content": message}
        previous_conversation = user.get("conversation", [])
        messages = [*previous_conversation, new_message]

        try:
            logger.info(
                f'Calling OpenAI API "{user.get(DatabaseKeys.User.CHOSEN_MODEL, "UNKNOWN")}" model'
            )
            self.total_responses_count += 1
            response = openai.ChatCompletion.create(
                model=user.get(DatabaseKeys.User.CHOSEN_MODEL, DEFAULT_MODEL.name),
                messages=messages,
            )
            choice = response.get("choices")[0]
            answer = choice.get("message").get("content")
            answer = answer.strip()
        except Exception as error:
            error_message = await handle_model_error(error)
        else:
            self.success_responses_count += 1
        finally:
            self.error_responses_count += 1

        if error_message is not None:
            error_info = {
                "user_id": user.get("id"),
                "message": message,
                "previous_conversation": previous_conversation,
                "response": response.to_dict() if response else None,
                "error_message": error_message,
                "timestamp": datetime.now(),
            }
            logger.error(error_message, error_info=error_info)

            return (
                error_message
                + f"\n\nУровень стабильности: {self.stability_percentage:.2f}%"
            )

        user["conversation"] = [*messages, {"role": "assistant", "content": answer}]

        Database().update_user_by_id(user)

        return answer

    @property
    def stability_percentage(self) -> float:
        if self.total_responses_count == 0:
            return 100.0

        return (self.success_responses_count / self.total_responses_count) * 100.0
