import abc

from pydantic import validator

from autogpt.core.configuration import SystemConfiguration
from autogpt.core.planning.schema import (
    LanguageModelClassification,
    LanguageModelPrompt,
    LanguageModelFunction
)

from autogpt.core.configuration import (
    Configurable,
    SystemConfiguration,
    SystemSettings,
    UserConfigurable,
)

from autogpt.core.resource.model_providers import (
    LanguageModelProvider,
    ModelProviderName,
    OpenAIModelName,
)

# class Planner(abc.ABC):
#     """Manages the agent's planning and goal-setting by constructing language model prompts."""
#
#     @staticmethod
#     @abc.abstractmethod
#     async def decide_name_and_goals(
#         user_objective: str,
#     ) -> LanguageModelResponse:
#         """Decide the name and goals of an Agent from a user-defined objective.
#
#         Args:
#             user_objective: The user-defined objective for the agent.
#
#         Returns:
#             The agent name and goals as a response from the language model.
#
#         """
#         ...
#
#     @abc.abstractmethod
#     async def plan(self, context: PlanningContext) -> LanguageModelResponse:
#         """Plan the next ability for the Agent.
#
#         Args:
#             context: A context object containing information about the agent's
#                        progress, result, memories, and feedback.
#
#
#         Returns:
#             The next ability the agent should take along with thoughts and reasoning.
#
#         """
#         ...
#
#     @abc.abstractmethod
#     def reflect(
#         self,
#         context: ReflectionContext,
#     ) -> LanguageModelResponse:
#         """Reflect on a planned ability and provide self-criticism.
#
#
#         Args:
#             context: A context object containing information about the agent's
#                        reasoning, plan, thoughts, and criticism.
#
#         Returns:
#             Self-criticism about the agent's plan.
#
#         """
#         ...


class PromptStrategiesConfiguration(SystemConfiguration):
    pass



class LanguageModelConfiguration(SystemConfiguration):
    """Struct for model configuration."""

    model_name: str = UserConfigurable()
    provider_name: ModelProviderName = UserConfigurable()
    temperature: float = UserConfigurable()


class PlannerConfiguration(SystemConfiguration):
    """Configuration for the Planner subsystem."""

    models: dict[LanguageModelClassification, LanguageModelConfiguration]

    @validator("models")
    def validate_models(cls, models):
        expected_keys = set(LanguageModelClassification)
        actual_keys = set(models.keys())

        if expected_keys != actual_keys:
            missing_keys = expected_keys - actual_keys
            raise ValueError(f"Missing keys in 'models': {missing_keys}")

        return models

class PlannerSettings(SystemSettings):
    """Settings for the Planner subsystem."""

    configuration: PlannerConfiguration



class PromptStrategy(abc.ABC):
    STRATEGY_NAME : str
    default_configuration: PromptStrategiesConfiguration

    @property
    @abc.abstractmethod
    def model_classification(self) -> LanguageModelClassification:
        ...

    @abc.abstractmethod
    def build_prompt(self, *_, **kwargs) -> LanguageModelPrompt:
        ...

    @abc.abstractmethod
    def parse_response_content(self, response_content: dict) -> dict:
        ...

class BasePromptStrategy (PromptStrategy):
    
    @property
    def model_classification(self) -> LanguageModelClassification:
        return self._model_classification
    
    
    # TODO : This implementation is shit :) 
    # + Move to BasePromptStrategy
    def get_functions(self) -> list[LanguageModelFunction]:
        return self._functions
        
    # TODO : This implementation is shit :) 
    # + Move to BasePromptStrategy
    def get_functions_names(self) -> list[str]:
       return [item.name for item in self._functions]
    #     re = [Re,Se ,Va]
        