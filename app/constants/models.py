from app.constants import AccessLevel
from app.dto import Model

DEFAULT_TEMPERATURE = 0.7
DEFAULT_MIN_ACCESS_LEVEL = AccessLevel.USER


class AvailableModels:
    # GPT3_5_TURBO = 'gpt-3.5-turbo'
    # GPT4 = 'gpt-4'
    # GPT4_32K = 'gpt-4-32k'
    #
    # TEXT_DAVINCI_003 = 'text-davinci-003'
    # CODE_DAVINCI_002 = 'code-davinci-002'
    #
    # ALL = [GPT3_5_TURBO, GPT4, GPT4_32K, TEXT_DAVINCI_003, CODE_DAVINCI_002]

    GPT3_5_TURBO = Model(
        name='gpt-3.5-turbo',
        min_access_level=DEFAULT_MIN_ACCESS_LEVEL,
        temperature=DEFAULT_TEMPERATURE,
        is_active=True,
    )

    GPT4 = Model(
        name='gpt-4',
        min_access_level=AccessLevel.USER,
        temperature=DEFAULT_TEMPERATURE,
    )