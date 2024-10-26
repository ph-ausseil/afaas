from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from AFAAS.interfaces.task.task import AbstractTask

from AFAAS.interfaces.tools.tool import AFAASBaseTool
from AFAAS.interfaces.adapters import (
    AbstractLanguageModelProvider,
    AbstractChatModelProvider,
    AbstractPromptConfiguration,
    AssistantChatMessage,
    ChatPrompt,
    CompletionModelFunction,
)
from AFAAS.interfaces.agent.main import BaseAgent
from AFAAS.interfaces.prompts.strategy import (
    AbstractPromptStrategy,
    DefaultParsedResponse,
    PromptStrategiesConfiguration,
)
from AFAAS.lib.sdk.logger import AFAASLogger
from AFAAS.lib.utils.json_schema import JSONSchema

from langchain_core.messages  import AIMessage , HumanMessage, SystemMessage , ChatMessage
LOG = AFAASLogger(name=__name__)


class SearchInfoStrategyFunctionNames(str, enum.Enum):
    QUERY_LANGUAGE_MODEL: str = "query_language_model"


class SearchInfoStrategyConfiguration(PromptStrategiesConfiguration):
    default_tool_choice: SearchInfoStrategyFunctionNames = (
        SearchInfoStrategyFunctionNames.QUERY_LANGUAGE_MODEL
    )
    task_context_length: int = 300
    temperature: float = 0.4


class SearchInfo_Strategy(AbstractPromptStrategy):
    default_configuration : SearchInfoStrategyConfiguration = SearchInfoStrategyConfiguration()
    STRATEGY_NAME = "search_info"

    def __init__(
        self,
        default_tool_choice: SearchInfoStrategyFunctionNames,
        temperature: float,  # if coding 0.05
        # top_p: Optional[float] ,
        # max_tokens : Optional[int] ,
        # frequency_penalty: Optional[float], # Avoid repeting oneselfif coding 0.3
        # presence_penalty : Optional[float], # Avoid certain subjects
        count=0,

        task_context_length: int = 300,
    ):
        self._count = count
        self.temperature = temperature or self.default_configuration.temperature
        self.default_tool_choice = default_tool_choice
        self.task_context_length = task_context_length

    def set_tools(
        self,
        task: AbstractTask,
        tools: list[AFAASBaseTool],
        **kwargs,
    ):
        self._tools: list[CompletionModelFunction] = []

        for tool in tools:
            self._tools.append(tool.dump())

    async def build_message(
        self,
        task: AbstractTask,
        agent: BaseAgent,
        query: str,
        reasoning: str,
        tools: list[AFAASBaseTool],
        **kwargs,
    ) -> ChatPrompt:
        LOG.debug("Building prompt for task : " + await task.debug_dump_str())
        self._task: AbstractTask = task
        smart_rag_param = {
            "query": query,
            "reasoning": reasoning,
            "tools": tools,
        }

        messages = []
        messages.append(
            SystemMessage(
                await self._build_jinja_message(
                    task=task,
                    template_name=f"{self.STRATEGY_NAME}.jinja",
                    template_params=smart_rag_param,
                )
            )
        )
        messages.append(SystemMessage(self.response_format_instruction()))


        return self.build_chat_prompt(messages=messages)

    def parse_response_content(
        self,
        response_content: AssistantChatMessage,
    ) -> DefaultParsedResponse:
        return self.default_parse_response_content(response_content=response_content)

    def response_format_instruction(self) -> str:
        return super().response_format_instruction()

    def get_llm_provider(self) -> AbstractChatModelProvider:
        return super().get_llm_provider()


    def get_prompt_config(self) -> AbstractPromptConfiguration:
        return AbstractPromptConfiguration(
            llm_model_name=self.get_llm_provider().__llmmodel_default__(),
            temperature=self.temperature,
        )
