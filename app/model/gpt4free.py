from typing import AsyncGenerator, TypeVar


from app.model.abstraction import ChatProvider
from app.constants import DatabaseKeys
from app.constants.defaults import DEFAULT_MODEL
from app.database import Database
from app.dto import User
from g4f.client import Client

T = TypeVar("T")


class GPT4FreeProvider(ChatProvider):

    _instance = None

    error_responses_count: int
    success_responses_count: int
    total_responses_count: int

    def on_created(self):
        self.error_responses_count = 0
        self.success_responses_count = 0
        self.total_responses_count = 0
        self.client = Client()

    async def create_answer(self, message: str, user: dict | User) -> str:
        if isinstance(user, User):
            user = user.to_dict()

        answer = ""

        new_message = {"role": "user", "content": message}
        previous_conversation = user.get("conversation", [])
        messages = [*previous_conversation, new_message]

        self.total_responses_count += 1

        response = self.client.chat.completions.create(
            model=user.get(DatabaseKeys.User.CHOSEN_MODEL, DEFAULT_MODEL.name),
            messages=messages,
        )
        print(response.choices[0].message.content)

        answer = response["message"]
        user["conversation"] = [*messages, answer]

        Database().update_user_by_id(
            user_id=user.get(DatabaseKeys.User.ID),
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
        chat_completion = self.client.chat.completions.create(
            # model=user.get(DatabaseKeys.User.CHOSEN_MODEL, DEFAULT_MODEL.name),
            model="llama-3.1-405b",
            messages=messages,
            stream=True,
        )

        for chunk in chat_completion:
            data = chunk.choices[0].delta.content or ""
            full_response += data
            yield data

        answer = {"role": "assistant", "content": full_response}
        user["conversation"] = [*messages, answer]

        Database().update_user_by_id(
            user_id=user[DatabaseKeys.User.ID],
            user_data=user,
        )

    def stability_percentage(self) -> float:
        if self.total_responses_count == 0:
            return 100.0

        return (self.success_responses_count / self.total_responses_count) * 100.0
