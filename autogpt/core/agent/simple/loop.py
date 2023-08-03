from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Callable, List

from typing_extensions import TypedDict

from autogpt.core.ability import AbilityResult
from autogpt.core.agent import BaseLoop, BaseLoopHook
from autogpt.core.planning import Task, TaskStatus
from autogpt.core.runner.client_lib.parser import (
    parse_ability_result,
    parse_agent_plan,
    parse_next_ability,
)

if TYPE_CHECKING:
    from autogpt.core.agent.base.agent import Agent


class SimpleLoop(BaseLoop):
    class AgentLoophooksDict(TypedDict):
        before_build_initial_plan: List[BaseLoopHook]
        after_build_initial_plan: List[BaseLoopHook]
        before_determine_next_ability: List[BaseLoopHook]
        after_determine_next_ability: List[BaseLoopHook]
        before_execute_next_ability: List[BaseLoopHook]
        before_build_initial_plan: List[BaseLoopHook]

    async def run(
        self,
        agent: Agent,
        hooks: AgentLoophooksDict,
        user_input_handler: Callable[[str], Awaitable[str]],
        user_message_handler: Callable[[str], Awaitable[str]],
    ) -> None:
        # step 1 : build initial plan
        self.handle_hooks("before_build_initial_plan", hooks, agent)
        plan = await self.build_initial_plan()
        self.handle_hooks("after_build_initial_plan", hooks, agent)
        # TODO : Move to hook
        user_message_handler(parse_agent_plan(plan))

        while self.isrunning:
            if self._active:
                # step 2 : determine_next_ability

                self.handle_hooks("before_determine_next_ability", hooks, agent)
                current_task, next_ability = await self.determine_next_ability(plan)
                self.handle_hooks("after_determine_next_ability", hooks, agent)
                # TODO : Move to hook
                user_message_handler(parse_next_ability(current_task, next_ability))
                user_input = await user_input_handler(
                    "Should the agent proceed with this ability?"
                )

                # step 3 : execute_next_ability

                self.handle_hooks("before_execute_next_ability", hooks, agent)
                ability_result = await self.execute_next_ability(user_input)
                self.handle_hooks("after_execute_next_ability", hooks, agent)
                # TODO : Move to hook after_execute_next_ability
                user_message_handler(parse_ability_result(ability_result))

    async def build_initial_plan(self) -> dict:
        plan = await self._agent._planning.make_initial_plan(
            agent_name=self._agent._configuration.name,
            agent_role=self._agent._configuration.role,
            agent_goals=self._agent._configuration.goals,
            abilities=self._agent._ability_registry.list_abilities(),
        )
        tasks = [Task.parse_obj(task) for task in plan.content["task_list"]]

        # TODO: Should probably do a step to evaluate the quality of the generated tasks,
        #  and ensure that they have actionable ready and acceptance criteria

        self._task_queue.extend(tasks)
        self._task_queue.sort(key=lambda t: t.priority, reverse=True)
        self._task_queue[-1].context.status = TaskStatus.READY
        return plan.content

    async def determine_next_ability(self, *args, **kwargs):
        if not self._task_queue:
            return {"response": "I don't have any tasks to work on right now."}

        self._agent._configuration.cycle_count += 1
        task = self._task_queue.pop()
        self._agent._logger.info(f"Working on task: {task}")

        task = await self._agent._evaluate_task_and_add_context(task)
        next_ability = await self._agent._choose_next_ability(
            task,
            self._agent._ability_registry.dump_abilities(),
        )
        self._current_task = task
        self._next_ability = next_ability.content
        return self._current_task, self._next_ability

    async def execute_next_ability(self, user_input: str, *args, **kwargs):
        if user_input == "y":
            ability = self._agent._ability_registry.get_ability(
                self._next_ability["next_ability"]
            )
            ability_response = await ability(**self._next_ability["ability_arguments"])
            await self._agent._update_tasks_and_memory(ability_response)
            if self._current_task.context.status == TaskStatus.DONE:
                self._completed_tasks.append(self._current_task)
            else:
                self._task_queue.append(self._current_task)
            self._current_task = None
            self._next_ability = None

            return ability_response.dict()
        else:
            raise NotImplementedError

    async def _evaluate_task_and_add_context(self, task: Task) -> Task:
        """Evaluate the task and add context to it."""
        if task.context.status == TaskStatus.IN_PROGRESS:
            # Nothing to do here
            return task
        else:
            self._agent._logger.debug(
                f"Evaluating task {task} and adding relevant context."
            )
            # TODO: Look up relevant memories (need working memory system)
            # TODO: Evaluate whether there is enough information to start the task (language model call).
            task.context.enough_info = True
            task.context.status = TaskStatus.IN_PROGRESS
            return task

    async def _choose_next_ability(self, task: Task, ability_schema: list[dict]):
        """Choose the next ability to use for the task."""
        self._agent._logger.debug(f"Choosing next ability for task {task}.")
        if task.context.cycle_count > self._agent._configuration.max_task_cycle_count:
            # Don't hit the LLM, just set the next action as "breakdown_task" with an appropriate reason
            raise NotImplementedError
        elif not task.context.enough_info:
            # Don't ask the LLM, just set the next action as "breakdown_task" with an appropriate reason
            raise NotImplementedError
        else:
            next_ability = await self._agent._planning.determine_next_ability(
                task, ability_schema
            )
            return next_ability

    async def _update_tasks_and_memory(self, ability_result: AbilityResult):
        self._current_task.context.cycle_count += 1
        self._current_task.context.prior_actions.append(ability_result)
        # TODO: Summarize new knowledge
        # TODO: store knowledge and summaries in memory and in relevant tasks
        # TODO: evaluate whether the task is complete

    def __repr__(self):
        return "SimpleLoop()"
