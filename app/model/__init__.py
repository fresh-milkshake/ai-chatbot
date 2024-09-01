"""
======= Model =======

This module contains:
 - models list (AvailableModels)
 - model parameters
 - default values
 - and other model-related constants

Also, it contains all the model-related logic, such as classes for interacting
with the model itself, and the logic for formatting model answers and storing
them in Redis as well as statistics for requests to the models.

Available build-in models "interfaces" at the moment:
    - GPT-3.5 Turbo
    - GPT-4
    - GPT-4 32k

See Also:
    :class:`app.model.external_model.ExternalLanguageModel`
    :class:`app.model.config.AvailableModels`
"""

from app.model.abstraction import ChatProvider
# from app.model.openai import OpenAIModels
# from app.model.gpt4free import Gpt4FreeProviders
from app.model.llama import LLaMAProvider



LanguageModel: ChatProvider = LLaMAProvider
