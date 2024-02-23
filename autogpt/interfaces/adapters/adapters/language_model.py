from __future__ import annotations

import abc
import enum
from typing import Callable, ClassVar, Protocol, Optional, Any

from pydantic import ConfigDict, BaseModel, Field
from AFAAS.lib.sdk.logger import AFAASLogger

from AFAAS.configs.schema import SystemConfiguration, Field
from AFAAS.interfaces.adapters.configuration import (
    BaseProviderBudget,
    BaseProviderCredentials,
    BaseProviderSettings,
    BaseProviderUsage,
)

LOG = AFAASLogger(name=__name__)

class ModelProviderService(str, enum.Enum):
    """A ModelService describes what kind of service the model provides."""

    EMBEDDING: str = "embedding"
    CHAT: str = "language"
    TEXT: str = "text"

class ModelProviderName(str, enum.Enum):
    OPENAI: str = "openai"

class BaseModelInfo(BaseModel):
    name: str
    service: ModelProviderService
    provider_name: ModelProviderName
    prompt_token_cost: float = 0.0
    completion_token_cost: float = 0.0


class BaseModelResponse(BaseModel):
    prompt_tokens : int
    completion_tokens: int
    llm_model_info: BaseModelInfo
    strategy: Optional[Any] = None # TODO: Should save the strategy used to get the response

    def __init__(self, **data: Any):
        super().__init__(**data)
        LOG.debug(f"BaseModelResponse does not save the strategy")


class BaseModelProviderConfiguration(SystemConfiguration):
    extra_request_headers: dict[str, str] = Field(default_factory=dict)
    retries_per_request: int = Field(default=10)
    maximum_retry: int = 1
    maximum_retry_before_default_function: int = 1


class BaseModelProviderCredentials(BaseProviderCredentials):
    api_key: str | None = Field(default=None)
    api_type: str | None = Field(default=None)
    api_base: str | None = Field(default=None)
    api_version: str | None = Field(default=None)
    deployment_id: str | None = Field(default=None)
    model_config = ConfigDict(extra="ignore")


class BaseModelProviderUsage(BaseProviderUsage):
    completion_tokens: int = 0
    prompt_tokens: int = 0
    total_tokens: int = 0

    def update_usage(
        self,
        model_response: BaseModelResponse,
    ) -> None:
        self.completion_tokens += model_response.completion_tokens
        self.prompt_tokens += model_response.prompt_tokens

        self.total_tokens += (
            model_response.completion_tokens + model_response.prompt_tokens

        )


class BaseModelProviderBudget(BaseProviderBudget):
    total_budget: float = Field()
    total_cost: float
    remaining_budget: float
    usage: BaseModelProviderUsage

    def update_usage_and_cost(
        self,
        model_response: BaseModelResponse,
    ) -> None:
        """Update the usage and cost of the provider."""
        llm_model_info = model_response.llm_model_info
        self.usage.update_usage(model_response)
        incurred_cost = (
            model_response.completion_tokens * llm_model_info.completion_token_cost
            + model_response.prompt_tokens
 * llm_model_info.prompt_token_cost
        )
        self.total_cost += incurred_cost
        if abs(self.remaining_budget) != float("inf"):
            self.remaining_budget -= incurred_cost


class BaseModelProviderSettings(BaseProviderSettings):
    configuration: BaseModelProviderConfiguration
    credentials: BaseModelProviderCredentials
    budget: BaseModelProviderBudget


class AbstractModelProvider(abc.ABC):
    default_settings: ClassVar[BaseModelProviderSettings]

    _configuration: BaseModelProviderConfiguration

    @abc.abstractmethod
    def count_tokens(self, text: str, model_name: str) -> int: ...

    @abc.abstractmethod
    def get_tokenizer(self, model_name: str) -> "ModelTokenizer": ...

    @abc.abstractmethod
    def get_token_limit(self, model_name: str) -> int: ...

    @abc.abstractmethod
    def get_remaining_budget(self) -> float: ...


class AbstractLanguageModelProvider(AbstractModelProvider):
    @abc.abstractmethod
    def has_oa_tool_calls_api(self, model_name: str) -> bool: ...

    @abc.abstractmethod
    def get_default_config(self) -> AbstractPromptConfiguration: ...

class ModelTokenizer(Protocol):
    @abc.abstractmethod
    def encode(self, text: str) -> list: ...

    @abc.abstractmethod
    def decode(self, tokens: list) -> str: ...

class AbstractPromptConfiguration(abc.ABC, SystemConfiguration):
    """Struct for model configuration."""

    llm_model_name: str = Field()
    temperature: float = Field()

