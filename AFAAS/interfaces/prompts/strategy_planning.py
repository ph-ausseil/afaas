from __future__ import annotations

import copy
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


from AFAAS.configs.schema import UserConfigurable
from AFAAS.interfaces.prompts.strategy import (
    RESPONSE_SCHEMA,
    AbstractPromptStrategy,
    PromptStrategiesConfiguration,
)
from AFAAS.lib.sdk.logger import AFAASLogger

LOG = AFAASLogger(name=__name__)


class PlanningPromptStrategiesConfiguration(PromptStrategiesConfiguration):
    DEFAULT_CHOOSE_ACTION_INSTRUCTION: str = (
        "Determine exactly one command to use next based on the given goals "
        "and the progress you have made so far, "
        "and respond using the JSON schema specified previously:"
    )
    DEFAULT_RESPONSE_SCHEMA = copy.deepcopy(RESPONSE_SCHEMA)

    response_schema: dict = UserConfigurable(
        default_factory=DEFAULT_RESPONSE_SCHEMA.to_dict
    )
    choose_action_instruction: str = UserConfigurable(
        default=DEFAULT_CHOOSE_ACTION_INSTRUCTION
    )
    use_functions_api: bool = UserConfigurable(default=False)

    #########
    # State #
    #########
    progress_summaries: dict[tuple[int, int], str] = {(0, 0): ""}


class AbstractPlanningPromptStrategy(AbstractPromptStrategy):
    def __init__(
        self,
        # temperature: float,  # if coding 0.05
        # top_p: Optional[float],
        # max_tokens: Optional[int],
        # frequency_penalty: Optional[float],  # Avoid repeting oneselfif coding 0.3
        # presence_penalty: Optional[float],  # Avoid certain subjects
        **kwargs,
    ):
        super().__init__()
