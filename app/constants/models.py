from app.constants import AccessLevel
from app.dto import Model

DEFAULT_TEMPERATURE = 1  # 0 - 2
DEFAULT_MIN_ACCESS_LEVEL = AccessLevel.USER


class AvailableModels:
    """
    Available models container.
    Models are stored as :class:`app.dto.Model` objects.
    """

    GPT3_5_TURBO = Model(
        name="gpt-3.5-turbo",
        min_access_level=DEFAULT_MIN_ACCESS_LEVEL,
        temperature=DEFAULT_TEMPERATURE,
        is_active=False,
    )

    GPT4o = Model(
        name="gpt-4o",
        min_access_level=AccessLevel.USER,
        temperature=DEFAULT_TEMPERATURE,
        is_active=False,
    )

    LLAMA3 = Model(
        name="llama3",
        min_access_level=AccessLevel.USER,
        temperature=DEFAULT_TEMPERATURE,
        is_active=False,
    )

    LLAMA3_1 = Model(
        name="llama3.1",
        min_access_level=AccessLevel.USER,
        temperature=DEFAULT_TEMPERATURE,
        is_active=True,
    )

    LLAVA = Model(
        name="llava",
        min_access_level=AccessLevel.PRIVILEGED_USER,
        temperature=DEFAULT_TEMPERATURE,
        is_active=False,
    )

    LLAMA2_UNCENSORED = Model(
        name="llama2-uncensored",
        min_access_level=AccessLevel.USER,
        temperature=DEFAULT_TEMPERATURE,
        is_active=True,
    )

    @classmethod
    def ALL(cls):
        models = []

        for attr in cls.__dict__:
            if attr.startswith("__") and attr.endswith("__"):
                continue
            models.append(cls.__dict__[attr])
        return models

    @staticmethod
    def filter_by_access_level(access_level: AccessLevel):
        """
        Filter available models by access level.

        Args:
            access_level: Access level to filter by.

        Returns:
            Filtered list of models.
        """
        return [
            model
            for model in AvailableModels.ALL()
            if model.min_access_level <= access_level
        ]

    @staticmethod
    def latest_free():
        """
        Get the latest free model.

        Returns:
            Latest free model.
        """
        return AvailableModels.LLAMA3_1
