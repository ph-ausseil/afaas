from logging import Logger
from autogpt.core.planning.base import BasePromptStrategy,PromptStrategiesConfiguration
from autogpt.core.agent.usercontext.strategies.refine_user_context import (
    RefineUserContextStrategy,
    RefineUserContextConfiguration,
    RefineUserContextFunctionNames
)

class StrategiesConfiguration(PromptStrategiesConfiguration):
    refine_user_context: RefineUserContextConfiguration 


class Strategies() :
    from autogpt.core.planning.base import BasePromptStrategy,PromptStrategy
    
    @staticmethod
    def get_strategies(logger = Logger) -> list[BasePromptStrategy] :
        return [
            RefineUserContextStrategy(logger = logger, **RefineUserContextStrategy.default_configuration.dict()),
        ]