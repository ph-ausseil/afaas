from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Callable, List, Dict

from typing_extensions import TypedDict

from autogpt.core.ability import AbilityResult
from autogpt.core.agent.base import BaseLoop, BaseLoopHook
from autogpt.core.planning import Task, TaskStatus
from autogpt.core.runner.client_lib.parser import (
    parse_ability_result,
    parse_agent_plan,
    parse_next_ability,
)

if TYPE_CHECKING:
    from autogpt.core.agent.base.agent import Agent

from autogpt.core.agent.usercontext.strategies import RefineUserContextFunctionNames


class UserContextLoop(BaseLoop):
    class LoophooksDict(BaseLoop.LoophooksDict):
        pass

    def __init__(self, agent: Agent) -> None:
        super().__init__(agent)
        self._active = False

    async def run(
        self,
        agent: Agent,
        hooks: LoophooksDict,
        user_input_handler: Callable[[str], Awaitable[str]],
        user_message_handler: Callable[[str], Awaitable[str]],
    ) -> dict:
        self._agent._logger.info(f"Running UserContextLoop")
        
        self.loop_count = 0
        user_input = ''
        # _is_running is important because it avoid having two concurent loop in the same agent (cf : Agent.run())

        user_objectives = self._agent.agent_goal_sentence 
        force_quite = False
        reformulated_goal = None
        while self._is_running:

            # if _active is false, then the loop is paused
            if self._active:
                self.loop_count += 1
                self._agent._logger.info(f"Starting loop iteration number {self.loop_count}")

                model_response = await self._agent._planning.execute_strategy(strategy_name = 'refine_user_context',
                force_quite = force_quite,
                user_objective = user_objectives
                )

                if  model_response.content['name'] == RefineUserContextFunctionNames.REFINE_REQUIREMENTS  :
                    input_dict = model_response.content 
                    reformulated_goal = model_response.content['reformulated_goal']
                    user_objectives = await user_input_handler(input_dict)
                elif model_response.content['name'] == RefineUserContextFunctionNames.REQUEST_SECOND_CONFIRMATION   :
                    input_dict = model_response.content 
                    user_objectives = await user_input_handler(input_dict)
                elif model_response.content['name'] == RefineUserContextFunctionNames.VALIDATE_GOAL  and reformulated_goal is not None :
                    self._agent._logger.info(f"Exiting UserContextLoop")
                    return_value = {'agent_goal_sentence' : reformulated_goal, 
                            'agent_goals' : model_response.content['goal_list']}
                    return return_value
                else : 
                    self._agent._logger.error(model_response.content)
                    raise Exception
                
                if user_objectives.lower() == 'y' and self.loop_count > 1:
                    force_quite = True
            
                self._agent.save_agent_in_memory()

    def __repr__(self):
        return "UserContextLoop()"
