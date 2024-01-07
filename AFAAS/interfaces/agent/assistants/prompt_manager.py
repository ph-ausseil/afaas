from __future__ import annotations

import platform
import time
from typing import TYPE_CHECKING, Any

from AFAAS.interfaces.agent.features.agentmixin import AgentMixin

if TYPE_CHECKING:
    from AFAAS.interfaces.prompts.strategy import (
    AbstractPromptStrategy)
    from AFAAS.interfaces.agent.main import BaseAgent

from AFAAS.interfaces.adapters import (
    AbstractChatModelProvider,
    AbstractChatModelResponse,
)
from AFAAS.lib.sdk.logger import AFAASLogger

LOG = AFAASLogger(name=__name__)


# FIXME: Find somewhere more appropriate
class SystemInfo(dict):
    os_info: str
    # provider : OpenAIProvider
    api_budget: float
    current_time: str

class BasePromptManager(AgentMixin):
    """Manages the agent's planning and goal-setting by constructing language model prompts."""

    def __init__(
        self,
    ) -> None:

        self._prompt_strategies = {}

    def add_strategies(self, strategies : list[AbstractPromptStrategy])->None : 
        for strategy in strategies:
            self._prompt_strategies[strategy.STRATEGY_NAME] = strategy

    def set_agent(self, agent: "BaseAgent"):
        if not hasattr(self, "_agent") or self._agent is None:
            super().set_agent(agent)
        self.load_strategies()

    def load_strategies(self) -> list[AbstractPromptStrategy]:

        from AFAAS.prompts import (
            AFAAS_SMART_RAG_Strategy,
            AfaasPostRagTaskUpdateStrategy,
            AfaasTaskRagStep2Strategy,
            AfaasTaskRagStep3Strategy,
            AutoCorrectionStrategy,
            BaseTaskSummary_Strategy,
            SearchInfo_Strategy,
            QueryLLMStrategy,
            load_all_strategies,
        )
        common_strategies = [AutoCorrectionStrategy(
                **AutoCorrectionStrategy.default_configuration.dict()
            ),
        AFAAS_SMART_RAG_Strategy(
               **AFAAS_SMART_RAG_Strategy.default_configuration.dict()
        ),
        BaseTaskSummary_Strategy(
                **BaseTaskSummary_Strategy.default_configuration.dict()
        ),
        AfaasTaskRagStep2Strategy(
                **AfaasTaskRagStep2Strategy.default_configuration.dict()
        ),
        AfaasTaskRagStep3Strategy(
                **AfaasTaskRagStep3Strategy.default_configuration.dict()
        ),
        AfaasPostRagTaskUpdateStrategy(
                **AfaasPostRagTaskUpdateStrategy.default_configuration.dict()
        ),
        SearchInfo_Strategy(
                **SearchInfo_Strategy.default_configuration.dict()
        ),
        QueryLLMStrategy(
                **QueryLLMStrategy.default_configuration.dict()
        )

        ]


        self._agent.__class__.__module__.rsplit('.', 1)[0]
        strategies : list[AbstractPromptStrategy] = []
        strategies += load_all_strategies()

        self.add_strategies(strategies = strategies + common_strategies)
        return self._prompt_strategies

    async def execute_strategy(self, strategy_name: str, **kwargs) -> AbstractChatModelResponse:
        """
        await simple_planner.execute_strategy('name_and_goals', user_objective='Learn Python')
        await simple_planner.execute_strategy('initial_plan', agent_name='Alice', agent_role='Student', agent_goals=['Learn Python'], tools=['coding'])
        await simple_planner.execute_strategy('initial_plan', agent_name='Alice', agent_role='Student', agent_goal_sentence=['Learn Python'], tools=['coding'])
        """
        if strategy_name not in self._prompt_strategies:
            raise ValueError(f"Invalid strategy name {strategy_name}")

        prompt_strategy: AbstractPromptStrategy = self._prompt_strategies[strategy_name]
        if not hasattr(prompt_strategy, "_agent") or prompt_strategy._agent is None:
            prompt_strategy.set_agent(agent=self._agent)

        kwargs.update(self.get_system_info(prompt_strategy))

        LOG.trace(
            f"Executing strategy : {prompt_strategy.STRATEGY_NAME}"
        )

        prompt_strategy.set_tools(**kwargs)

        return await self.send_to_chatmodel(prompt_strategy, **kwargs)

    async def send(self, prompt_strategy : AbstractPromptStrategy, **kwargs):
        llm_provider = prompt_strategy.get_llm_provider()
        if (isinstance(llm_provider, AbstractChatModelProvider)):
            return await self.send_to_chatmodel(prompt_strategy, **kwargs)
        else :
            return await self.send_to_languagemodel(prompt_strategy, **kwargs)

    async def send_to_languagemodel(
        self,
        prompt_strategy: AbstractPromptStrategy,
        **kwargs,
    ) :
        raise NotImplementedError("Language Model not implemented")

    async def send_to_chatmodel(
        self,
        prompt_strategy: AbstractPromptStrategy,
        **kwargs,
    ) -> AbstractChatModelResponse:

        provider : AbstractChatModelProvider = prompt_strategy.get_llm_provider()
        model_configuration = prompt_strategy.get_prompt_config().dict()

        LOG.trace(f"Using model configuration: {model_configuration}")

        # FIXME : Check if Removable
        template_kwargs = self.get_system_info(prompt_strategy)
        template_kwargs.update(kwargs)
        template_kwargs.update(model_configuration)

        prompt = await prompt_strategy.build_message(**template_kwargs)

        response: AbstractChatModelResponse = await provider.create_chat_completion(
            chat_messages=prompt.messages,
            tools=prompt.tools,
            **model_configuration,
            completion_parser=prompt_strategy.parse_response_content,
            tool_choice=prompt.tool_choice,
            default_tool_choice=prompt.default_tool_choice,
        )

        response.chat_messages = prompt.messages
        response.system_prompt = prompt.messages[0].content
        return response

    def get_system_info(self, strategy: AbstractPromptStrategy) -> SystemInfo:
        provider = strategy.get_llm_provider()
        template_kwargs = {
            "os_info": self.get_os_info(),
            "api_budget": provider.get_remaining_budget(),
            "current_time": time.strftime("%c"),
        }
        return template_kwargs

    @staticmethod
    def get_os_info() -> str:

        os_name = platform.system()
        if os_name != "Linux" :
            return platform.platform(terse=True)
        else :
            import distro
            return distro.name(pretty=True)

    def __repr__(self) -> str | tuple[Any, ...]:
        return f"{__class__.__name__}():\nAgent:{self._agent.agent_id}\nStrategies:{self._prompt_strategies}"
