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
        is_active=True,
    )

    GPT4 = Model(
        name="gpt-4",
        min_access_level=AccessLevel.USER,
        temperature=DEFAULT_TEMPERATURE,
        is_active=True,
    )

    LATEST_LLAMA = Model(
        name="llama-2-7b-chat",
        min_access_level=AccessLevel.USER,
        temperature=DEFAULT_TEMPERATURE,
        is_active=True,
    )
    
    GPT4FREE = Model(
        name="gpt4free",
        min_access_level=AccessLevel.USER,
        temperature=DEFAULT_TEMPERATURE,
        is_active=True,
    )

    ALL = [GPT3_5_TURBO, GPT4, LATEST_LLAMA]

    @staticmethod
    def filter_by_access_level(access_level: AccessLevel):
        """
        Filter available models by access level.

        Args:
            access_level: Access level to filter by.

        Returns:
            Filtered list of models.
        """
        return list(
            filter(
                lambda model: model.min_access_level <= access_level,
                AvailableModels.ALL,
            )
        )
