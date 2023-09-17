import logging
import platform
import time


from autogpt.core.configuration import (
    Configurable,
    SystemConfiguration,
    SystemSettings,
    UserConfigurable,
)
from autogpt.core.planning.base import BasePromptStrategy,PromptStrategy , PromptStrategiesConfiguration, PlannerConfiguration, PlannerSettings, LanguageModelConfiguration
from autogpt.core.planning.schema import (
    LanguageModelClassification,
    LanguageModelResponse,
    Task,
)
from autogpt.core.resource.model_providers import (
    LanguageModelProvider,
    ModelProviderName,
    OpenAIModelName,
)
from autogpt.core.workspace import Workspace


class SimplePlanner(Configurable):
    """Manages the agent's planning and goal-setting by constructing language model prompts."""

    default_settings = PlannerSettings(
        name="planner",
        description="Manages the agent's planning and goal-setting by constructing language model prompts.",
        configuration=PlannerConfiguration(
            models={
                LanguageModelClassification.FAST_MODEL_4K: LanguageModelConfiguration(
                    model_name=OpenAIModelName.GPT3,
                    provider_name=ModelProviderName.OPENAI,
                    temperature=0.9,
                ),
                LanguageModelClassification.FAST_MODEL_16K: LanguageModelConfiguration(
                    model_name=OpenAIModelName.GPT3_16K,
                    provider_name=ModelProviderName.OPENAI,
                    temperature=0.9,
                ),
                LanguageModelClassification.FAST_MODEL_FINE_TUNED_4K: LanguageModelConfiguration(
                    model_name=OpenAIModelName.GPT3_FINE_TUNED,
                    provider_name=ModelProviderName.OPENAI,
                    temperature=0.9,
                ),
                LanguageModelClassification.SMART_MODEL_8K: LanguageModelConfiguration(
                    model_name=OpenAIModelName.GPT4,
                    provider_name=ModelProviderName.OPENAI,
                    temperature=0.9,
                ),
                LanguageModelClassification.SMART_MODEL_32K: LanguageModelConfiguration(
                    model_name=OpenAIModelName.GPT4_32K,
                    provider_name=ModelProviderName.OPENAI,
                    temperature=0.9,
                ),
            },
        ),
    )

    def __init__(
        self,
        settings: PlannerSettings,
        logger: logging.Logger,
        model_providers: dict[ModelProviderName, LanguageModelProvider],
        strategies: dict[str, PromptStrategy],
        workspace: Workspace = None,  # Workspace is not available during bootstrapping.
    ) -> None:
        super().__init__(settings, logger)
        # self._configuration = settings.configuration
        # self._logger = logger
        self._workspace = workspace

        self._providers: dict[LanguageModelClassification, LanguageModelProvider] = {}
        for model, model_config in self._configuration.models.items():
            self._providers[model] = model_providers[model_config.provider_name]

        # self._prompt_strategies = settings.planning.configuration.prompt_strategies 
        
        # self._prompt_strategies = strategies
        # self._prompt_strategies = {
        #     "name_and_goals": strategies.NameAndGoals(
        #         **self._configuration.prompt_strategies.name_and_goals.dict()
        #     ),
        #     "initial_plan": strategies.InitialPlan(
        #         **self._configuration.prompt_strategies.initial_plan.dict()
        #     ),
        #     "next_ability": strategies.NextAbility(
        #         **self._configuration.prompt_strategies.next_ability.dict()
        #     ),
        # }

        ##
        ## REMOVED DEFAULT STRATEGIES
        ##

        # default_strategies = {
        #     "name_and_goals": strategies.NameAndGoals(),
        #     "initial_plan": strategies.InitialPlan(),
        #     "next_ability": strategies.NextAbility(),
        # }


        # default_strategies = {
        #     "name_and_goals": strategies.name_and_goals,
        #     "initial_plan": strategies.initial_plan,
        #     "next_ability": strategies.next_ability,
        # }

        # if strategies is not None:
        #     default_strategies.update(strategies)

        # self._prompt_strategies = default_strategies

        self._prompt_strategies ={}
        for strategy in strategies : 
            self._prompt_strategies[strategy.STRATEGY_NAME] = strategy

        logger.debug(f"Planner created with strategies : {self._prompt_strategies}")
        # self._prompt_strategies = strategies

    async def execute_strategy(self, strategy_name: str, **kwargs) -> LanguageModelResponse:
        """
        await simple_planner.execute_strategy('name_and_goals', user_objective='Learn Python')
        await simple_planner.execute_strategy('initial_plan', agent_name='Alice', agent_role='Student', agent_goals=['Learn Python'], abilities=['coding'])
        await simple_planner.execute_strategy('initial_plan', agent_name='Alice', agent_role='Student', agent_goal_sentence=['Learn Python'], abilities=['coding'])
        """
        if strategy_name not in self._prompt_strategies:
            raise ValueError(f"Invalid strategy name {strategy_name}")

        prompt_strategy = self._prompt_strategies[strategy_name]
        return await self.chat_with_model(prompt_strategy, **kwargs)
    
    # async def decide_name_and_goals(self, user_objective: str) -> LanguageModelResponse:
    #     return await self.chat_with_model(
    #         self._prompt_strategies["name_and_goals"],
    #         user_objective=user_objective,
    #     )

    # async def make_initial_plan(
    #     self,
    #     agent_name: str,
    #     agent_role: str,
    #     agent_goals: list[str],
    #     agent_goal_sentence: str,
    #     abilities: list[str],
    # ) -> LanguageModelResponse:
    #     return await self.chat_with_model(
    #         self._prompt_strategies["initial_plan"],
    #         agent_name=agent_name,
    #         agent_role=agent_role,
    #         agent_goals=agent_goals,
    #         agent_goals=agent_goal_sentence,
    #         abilities=abilities,
    #     )

    # async def determine_next_ability(
    #     self,
    #     task: Task,
    #     ability_schema: list[dict],
    # ):
    #     return await self.chat_with_model(
    #         self._prompt_strategies["next_ability"],
    #         task=task,
    #         ability_schema=ability_schema,
    #     )

    async def chat_with_model(
        self,
        prompt_strategy: PromptStrategy,
        **kwargs,
    ) -> LanguageModelResponse:
        model_classification = prompt_strategy.model_classification
        model_configuration = self._configuration.models[model_classification].dict()
        self._logger.debug(f"Using model configuration: {model_configuration}")
        del model_configuration["provider_name"]
        provider = self._providers[model_classification]

        template_kwargs = self._make_template_kwargs_for_strategy(prompt_strategy)
        template_kwargs.update(kwargs)
        prompt = prompt_strategy.build_prompt(**template_kwargs)

        self._logger.debug(f"Using prompt:\n{prompt}\n\n")
        response = await provider.create_language_completion(
            model_prompt=prompt.messages,
            functions=prompt.functions,
            **model_configuration,
            completion_parser=prompt_strategy.parse_response_content,
            function_call = prompt.function_call,
            default_function_call = prompt.default_function_call
        )
        return LanguageModelResponse.parse_obj(response.dict())

    def _make_template_kwargs_for_strategy(self, strategy: PromptStrategy):
        provider = self._providers[strategy.model_classification]
        template_kwargs = {
            "os_info": get_os_info(),
            "api_budget": provider.get_remaining_budget(),
            "current_time": time.strftime("%c"),
        }
        return template_kwargs

# FIXME : Only import distro when required
import distro
def get_os_info() -> str:
    os_name = platform.system()
    os_info = (
        platform.platform(terse=True)
        if os_name != "Linux"
        else distro.name(pretty=True)
    )
    return os_info
