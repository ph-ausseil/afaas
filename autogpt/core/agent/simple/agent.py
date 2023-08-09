from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING, Awaitable, Callable, List

from autogpt.core.ability import AbilityResult, SimpleAbilityRegistry
from autogpt.core.agent.base.agent import Agent
from autogpt.core.agent.simple.loop import SimpleLoop
from autogpt.core.agent.simple.models import (
    SimpleAgentConfiguration,
    SimpleAgentSettings,
    SimpleAgentSystems,
    SimpleAgentSystemSettings,
)
from autogpt.core.configuration import Configurable
from autogpt.core.memory.base import Memory
from autogpt.core.planning import SimplePlanner, Task, TaskStatus
from autogpt.core.plugin.simple import PluginLocation, PluginStorageFormat
from autogpt.core.resource.model_providers import OpenAIProvider
from autogpt.core.workspace.simple import SimpleWorkspace

if TYPE_CHECKING:
    from autogpt.core.agent.base.loop import BaseLoopHook


class SimpleAgent(Agent, Configurable):
    ################################################################################
    ##################### REFERENCE SETTINGS FOR FACTORY ###########################
    ################################################################################

    AGENT_SYSTEM_SETINGS = SimpleAgentSystemSettings
    AGENT_CONFIGURATION = SimpleAgentConfiguration
    AGENT_SETTINGS = SimpleAgentSettings
    AGENT_SYSTEMS = SimpleAgentSystems

    default_settings = SimpleAgentSystemSettings(
        name="simple_agent",
        description="A simple agent.",
        configuration=SimpleAgentConfiguration(
            agent_name="Entrepreneur-GPT",
            agent_role=(
                "An AI designed to autonomously develop and run businesses with "
                "the sole goal of increasing your net worth."
            ),
            agent_goals=[
                "Increase net worth",
                "Grow Twitter Account",
                "Develop and manage multiple businesses autonomously",
            ],
            cycle_count=0,
            max_task_cycle_count=3,
            creation_time="",
            systems=SimpleAgentSystems(
                ability_registry=PluginLocation(
                    storage_format=PluginStorageFormat.INSTALLED_PACKAGE,
                    storage_route="autogpt.core.ability.SimpleAbilityRegistry",
                ),
                memory=PluginLocation(
                    storage_format=PluginStorageFormat.INSTALLED_PACKAGE,
                    storage_route="autogpt.core.memory.Memory",
                ),
                openai_provider=PluginLocation(
                    storage_format=PluginStorageFormat.INSTALLED_PACKAGE,
                    storage_route="autogpt.core.resource.model_providers.OpenAIProvider",
                ),
                planning=PluginLocation(
                    storage_format=PluginStorageFormat.INSTALLED_PACKAGE,
                    storage_route="autogpt.core.planning.SimplePlanner",
                ),
                workspace=PluginLocation(
                    storage_format=PluginStorageFormat.INSTALLED_PACKAGE,
                    storage_route="autogpt.core.workspace.SimpleWorkspace",
                ),
            ),
        ),
    )

    def __init__(
        self,
        settings: SimpleAgentSystemSettings,
        logger: logging.Logger,
        ability_registry: SimpleAbilityRegistry,
        memory: Memory,
        openai_provider: OpenAIProvider,
        workspace: SimpleWorkspace,
        planning: SimplePlanner,
        user_id: uuid.UUID,
        agent_id: uuid.UUID = None,
    ):
        super().__init__(
        settings,
        logger,
        ability_registry,
        memory,
        workspace,
        user_id,
        agent_id,
        )

        # These are specific
        self._openai_provider = openai_provider
        self._planning = planning

        self.agent_role = settings.configuration.agent_role
        self.agent_goals = settings.configuration.agent_goals
        self.agent_name = settings.configuration.agent_name

        logger.debug("MID INIT  : SimpleAgent.__init.__ : self\n")
        logger.debug(self)

        # TODO Will provide another PR with the logic migrated to SimpleLoop once approved
        # self.default_callback = {
        #     #'a_hook_key' = MyCallable(arg)
        # }

        self._loop = SimpleLoop(
            agent=self
        )
        
        # NOTE : MOVE ADD HOOD TO BaseLoop

        #self.add_hook(name: str, hook: BaseLoopHook, uuid: uuid.UUID)
        #self.add_hook(name: str, hook: BaseLoopHook, uuid: uuid.UUID)
        #self.add_hook(name: str, hook: BaseLoopHook, uuid: uuid.UUID)
        #self.add_hook(name: str, hook: BaseLoopHook, uuid: uuid.UUID)

    def loophooks(self) -> List[SimpleLoop.LoophooksDict]:
        if not self._loophooks:
            self._loophooks = []
        return self._loophooks

    def loop(self) -> SimpleLoop:
        return self._loop 
    
    def add_hook(self, name: str, hook: BaseLoopHook, uuid: uuid.UUID):
        super().add_hook(self, name, hook, uuid)


        
    # @property
    # def default_callback(self, hook_name: str, result: Any) -> None:
    #     return None

    # @default_callback.setter
    # def default_callback(self, hook_name: str, result: Any) -> None:
    #     return None

    ################################################################################
    ####### SIMPLE AGENT IS AN AGENT SPECIALIZED IN PLANNING #######################
    ################################################################################


    async def build_initial_plan(self) -> dict:
        plan = await self._planning.make_initial_plan(
            agent_name=self._configuration.agent_name,
            agent_role=self._configuration.agent_role,
            agent_goals=self._configuration.agent_goals,
            abilities=self._ability_registry.list_abilities(),
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

        self._configuration.cycle_count += 1
        task = self._task_queue.pop()
        self._logger.info(f"Working on task: {task}")

        task = await self._evaluate_task_and_add_context(task)
        next_ability = await self._choose_next_ability(
            task,
            self._ability_registry.dump_abilities(),
        )

        if next_ability.content != None : 
            self._current_task = task
            self._next_ability = next_ability.content
            return self._current_task, self._next_ability
        else : 
            return_var , second_return_var = await self.determine_next_ability() 
            return return_var , second_return_var 

    async def execute_next_ability(self, user_input: str, *args, **kwargs):
        if user_input == "y":
            ability = self._ability_registry.get_ability(
                self._next_ability["next_ability"]
            )
            ability_response = await ability(**self._next_ability["ability_arguments"])
            await self._update_tasks_and_memory(ability_response)
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
            self._logger.debug(f"Evaluating task {task} and adding relevant context.")
            # TODO: Look up relevant memories (need working memory system)
            # TODO: Evaluate whether there is enough information to start the task (language model call).
            task.context.enough_info = True
            task.context.status = TaskStatus.IN_PROGRESS
            return task

    async def _choose_next_ability(self, task: Task, ability_schema: list[dict]):
        """Choose the next ability to use for the task."""
        self._logger.debug(f"Choosing next ability for task {task}.")
        if task.context.cycle_count > self._configuration.max_task_cycle_count:
            # Don't hit the LLM, just set the next action as "breakdown_task" with an appropriate reason
            raise NotImplementedError
        elif not task.context.enough_info:
            # Don't ask the LLM, just set the next action as "breakdown_task" with an appropriate reason
            raise NotImplementedError
        else:
            next_ability = await self._planning.determine_next_ability(
                task, ability_schema
            )
            return next_ability

    async def _update_tasks_and_memory(self, ability_result: AbilityResult):
        self._current_task.context.cycle_count += 1
        self._current_task.context.prior_actions.append(ability_result)
        # TODO: Summarize new knowledge
        # TODO: store knowledge and summaries in memory and in relevant tasks
        # TODO: evaluate whether the task is complete

    ################################################################################
    ################################ LOOP MANAGEMENT################################
    ################################################################################

    async def run(
        self,
        user_input_handler: Callable[[str], Awaitable[str]],
        user_message_handler: Callable[[str], Awaitable[str]],
        goal: str,
    ):
        super.run(
            user_input_handler=user_input_handler,
            user_message_handler=user_message_handler,
            goal=goal,
        )

    async def start(
        self,
        user_input_handler: Callable[[str], Awaitable[str]],
        user_message_handler: Callable[[str], Awaitable[str]],
    ):
        return_var = await super().start(
            agent=self,
            user_input_handler=user_input_handler,
            user_message_handler=user_message_handler,
        )
        return return_var

    async def stop(
        self,
        user_input_handler: Callable[[str], Awaitable[str]],
        user_message_handler: Callable[[str], Awaitable[str]],
    ):
        return_var = await super().stop(
            agent=self,
            user_input_handler=user_input_handler,
            user_message_handler=user_message_handler,
        )
        return return_var

    ################################################################################
    ################################FACTORY SPECIFIC################################
    ################################################################################


    @classmethod
    def get_agent_from_settings(
        cls,
        agent_settings: SimpleAgentSettings,
        logger: logging.Logger,
    ) -> Agent:
        agent_settings, agent_args = super().get_agent_from_settings(
            agent_settings=agent_settings, 
            logger=logger
        )
        agent_args["openai_provider"] = cls._get_system_instance(
            "openai_provider",
            agent_settings,
            logger,
        )
        agent_args["planning"] = cls._get_system_instance(
            "planning",
            agent_settings,
            logger,
            model_providers={"openai": agent_args["openai_provider"]},
        )

        # NOTE : Can't be moved to super() because require agent_args["openai_provider"]
        agent_args["ability_registry"] = cls._get_system_instance(
            "ability_registry",
            agent_settings,
            logger,
            workspace=agent_args["workspace"],
            memory=agent_args["memory"],
            model_providers={"openai": agent_args["openai_provider"]},
        )
        return cls(**agent_args)

    @classmethod
    async def determine_agent_name_and_goals(
        cls,
        user_objective: str,
        agent_settings: SimpleAgentSettings,
        logger: logging.Logger,
    ) -> dict:
        logger.debug("Loading OpenAI provider.")
        provider: OpenAIProvider = cls._get_system_instance(
            "openai_provider",
            agent_settings,
            logger=logger,
        )
        logger.debug("Loading agent planner.")
        agent_planner: SimplePlanner = cls._get_system_instance(
            "planning",
            agent_settings,
            logger=logger,
            model_providers={"openai": provider},
        )
        logger.debug("determining agent name and goals.")
        model_response = await agent_planner.decide_name_and_goals(
            user_objective,
        )

        return model_response.content

    ################################################################################
    ################################ DB INTERACTIONS ################################
    ################################################################################
    
    @classmethod
    def get_agentsetting_list_from_memory(self, user_id: uuid.UUID, logger: logging.Logger ) -> list[SimpleAgentSettings]:
        from autogpt.core.memory.base import (
            Memory,
            MemoryConfig,
            MemorySettings,
        )
        from autogpt.core.memory.table.base import AgentsTable, BaseTable
        """Warning !!!
        Returns a list of agent settings not a list of agent

        Returns:
            _type_: _description_
        """
        
        memory_settings = MemorySettings(configuration=MemoryConfig())

        memory = Memory.get_adapter(memory_settings= memory_settings, logger=logger)
        agent_table : AgentsTable  =memory.get_table("agents")
       
        filter = BaseTable.FilterDict({
                                        "user_id" : 
                                       [BaseTable.FilterItem(value=str(user_id), operator= BaseTable.Operators.EQUAL_TO)]
                                       } 
                                       )
        agent_list = agent_table.list(filter = filter)
        return agent_list
   
    @classmethod
    def get_agent_from_memory(cls, 
                              agent_settings : SimpleAgentSettings, 
                              agent_id: uuid.UUID, 
                              user_id: uuid.UUID, 
                              logger: logging.Logger ) -> Agent:
        from autogpt.core.memory.base import (
            Memory,
        )
        from autogpt.core.memory.table.base import AgentsTable

        # memory_settings = MemorySettings(configuration=agent_settings.memory)
        memory_settings = agent_settings.memory

        memory = Memory.get_adapter(memory_settings= memory_settings, logger=logger)
        agent_table : AgentsTable  = memory.get_table("agents" )
        agent = agent_table.get(agent_id= str(agent_id), user_id=str(user_id))
        
        if not agent :
            return None
        agent = SimpleAgent.get_agent_from_settings(
            agent_settings=agent_settings,
            logger=logger,
        )
        return agent

    def __repr__(self):
        return "SimpleAgent()"
