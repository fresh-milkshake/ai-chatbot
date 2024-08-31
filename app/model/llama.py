import asyncio
from dataclasses import dataclass
from typing import AsyncGenerator, Generic, TypeVar, Dict
from abc import ABC, abstractmethod

from loguru import logger
from telegram import Update

from app.constants import DatabaseKeys
from app.constants.defaults import DEFAULT_MODEL
from app.database import Database
from app.dto import User
from app.utils import Singleton
import ollama

T = TypeVar("T")


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


class LLaMAProvider(Singleton, ABC):

    _instance = None

    error_responses_count: int
    success_responses_count: int
    total_responses_count: int

    def on_created(self):
        self.error_responses_count = 0
        self.success_responses_count = 0
        self.total_responses_count = 0

    async def create_answer(self, message: str, user: dict | User) -> str:
        if isinstance(user, User):
            user = user.to_dict()

        error_message = None
        response = None
        answer = ""

        new_message = {"role": "user", "content": message}
        previous_conversation = user.get("conversation", [])
        messages = [*previous_conversation, new_message]

        self.total_responses_count += 1

        response = ollama.chat(
            model=user.get(DatabaseKeys.User.CHOSEN_MODEL, DEFAULT_MODEL.name),
            messages=messages,
            stream=False,
        )

        answer = response["message"]
        user["conversation"] = [*messages, answer]

        Database().update_user_by_id(
            user_id=user.get(DatabaseKeys.User.UNIQUE_ID),
            user_data=user,
        )

        return answer["content"].strip()

    async def stream_answer(
        self, message: str, user: dict | User
    ) -> AsyncGenerator[str, None]:
        if isinstance(user, User):
            user = user.to_dict()

        new_message = {"role": "user", "content": message}
        previous_conversation = user.get("conversation", [])
        messages = [*previous_conversation, new_message]

        self.total_responses_count += 1

        full_response = ""
        for chunk in ollama.chat(
            model=user.get(DatabaseKeys.User.CHOSEN_MODEL, DEFAULT_MODEL.name),
            messages=messages,
            stream=True,
        ):
            if chunk["message"]["content"]:
                full_response += chunk["message"]["content"]
                yield chunk["message"]["content"]

        answer = {"role": "assistant", "content": full_response}
        user["conversation"] = [*messages, answer]

        Database().update_user_by_id(
            user_id=user.get(DatabaseKeys.User.UNIQUE_ID),
            user_data=user,
        )

    def stability_percentage(self) -> float:
        if self.total_responses_count == 0:
            return 100.0

        return (self.success_responses_count / self.total_responses_count) * 100.0
