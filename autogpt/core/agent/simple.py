import logging
import uuid
from pathlib import Path
from typing import Any

from autogpt.core.ability import AbilityResult, SimpleAbilityRegistry
from autogpt.core.agent.base import (
    AgentConfiguration,
    AgentSettings,
    AgentSystems,
    AgentSystemSettings,
    BaseAgent,
)
from autogpt.core.configuration import Configurable

#from autogpt.core.memory import SimpleMemory
from autogpt.core.memory.base import Memory
from autogpt.core.planning import SimplePlanner, Task, TaskStatus
from autogpt.core.plugin.simple import (
    PluginLocation,
    PluginStorageFormat,
    SimplePluginService,
)
from autogpt.core.resource.model_providers import OpenAIProvider
from autogpt.core.workspace.simple import SimpleWorkspace


class SimpleAgent(BaseAgent, Configurable):
    default_settings = AgentSystemSettings(
        name="simple_agent",
        description="A simple agent.",
        configuration=AgentConfiguration(
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
            user_id=None,
            agent_id=None,
            systems=AgentSystems(
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
                user_id=None,
                agent_id=None,
            ),
        ),
        user_id=None,
        agent_id=None,
    )

    def __init__(
        self,
        settings: AgentSystemSettings,
        logger: logging.Logger,
        ability_registry: SimpleAbilityRegistry,
        memory: Memory,
        openai_provider: OpenAIProvider,
        planning: SimplePlanner,
        workspace: SimpleWorkspace,
        user_id: uuid.UUID,
        agent_id: uuid.UUID = None,
    ):
        self._configuration = settings.configuration
        self._logger = logger
        self._ability_registry = ability_registry
        self._memory = memory
        # FIXME: Need some work to make this work as a dict of providers
        #  Getting the construction of the config to work is a bit tricky
        self._openai_provider = openai_provider
        self._planning = planning
        self._workspace = workspace
        self._task_queue = []
        self._completed_tasks = []
        self._current_task = None
        self._next_ability = None
        self.agent_role = settings.configuration.agent_role
        self.agent_goals = settings.configuration.agent_goals
        self.agent_name = settings.configuration.agent_name
        self.user_id = user_id
        self.agent_id = agent_id

    @classmethod
    def create_agent(cls,
        agent_settings: AgentSettings,
        logger: logging.Logger,) -> uuid.UUID:
        """Create a new agent."""
        cls._create_workspace(agent_settings=agent_settings, logger=logger)
        agent_id = cls.create_agent_in_memory(agent_settings=agent_settings, 
                                              logger=logger,
                                              user_id = agent_settings.user_id)
        return agent_id

    @classmethod
    def _create_workspace(
        cls,
        agent_settings: AgentSettings,
        logger: logging.Logger,
    ):
        from autogpt.core.workspace import SimpleWorkspace
        return SimpleWorkspace.create_workspace(
            user_id=agent_settings.user_id, 
            agent_id=agent_settings.agent_id,  
            settings = agent_settings, 
            logger=logger)


    @classmethod
    def get_agent_from_settings(
        cls,
        agent_settings: AgentSettings,
        logger: logging.Logger,
    ) -> "SimpleAgent":
        #agent_settings = SimpleWorkspace.load_agent_settings(workspace_path)
        #systems = agent_settings['agent']['configuration']['systems']
        if not isinstance(agent_settings, AgentSettings):
            agent_settings: AgentSettings = agent_settings
        agent_args = {}

        agent_args["settings"] = agent_settings.agent
        agent_args["logger"] = logger
        agent_args["workspace"] = cls._get_system_instance(
            "workspace",
            agent_settings,
            logger,
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

        from autogpt.core.memory.base import Memory, MemoryAdapterType, MemoryConfig
        config = MemoryConfig(
            memory_adapter=MemoryAdapterType.NOSQL_JSON_FILE,
            json_file_path=str(Path("~/auto-gpt/data/").expanduser().resolve())
        )
        agent_args["memory"] =  Memory.get_adapter(config= config, logger=logger)
        agent_args['user_id'] = agent_settings.user_id

        agent_args["ability_registry"] = cls._get_system_instance(
            "ability_registry",
            agent_settings,
            logger,
            workspace=agent_args["workspace"],
            memory=agent_args["memory"],
            model_providers={"openai": agent_args["openai_provider"]},
        )

        return cls(**agent_args)

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

    def __repr__(self):
        return "SimpleAgent()"

    ################################################################
    # Factory interface for agent bootstrapping and initialization #
    ################################################################

    @classmethod
    def build_user_configuration(cls) -> dict[str, Any]:
        """Build the user's configuration."""
        configuration_dict = {
            "agent": cls.get_user_config(),
        }

        system_locations = configuration_dict["agent"]["configuration"]["systems"]
        for system_name, system_location in system_locations.items():
            system_class = SimplePluginService.get_plugin(system_location)
            configuration_dict[system_name] = system_class.get_user_config()
        configuration_dict = _prune_empty_dicts(configuration_dict)
        return configuration_dict

    @classmethod
    def compile_settings(
        cls, logger: logging.Logger, user_configuration: dict
    ) -> AgentSettings:
        """Compile the user's configuration with the defaults."""
        logger.debug("Processing agent system configuration.")
        configuration_dict = {
            "agent": cls.build_agent_configuration(
                user_configuration.get("agent", {})
            ).dict(),
        }

        system_locations = configuration_dict["agent"]["configuration"]["systems"]

        # Build up default configuration
        for system_name, system_location in system_locations.items():
            if system_location is not None and not isinstance(system_location, uuid.UUID):
                logger.debug(f"Compiling configuration for system {system_name}")
                system_class = SimplePluginService.get_plugin(system_location)
                configuration_dict[system_name] = system_class.build_agent_configuration(
                    user_configuration.get(system_name, {})
                ).dict()
            else :
                configuration_dict[system_name] = system_location
        return AgentSettings.parse_obj(configuration_dict)

    @classmethod
    async def determine_agent_name_and_goals(
        cls,
        user_objective: str,
        agent_settings: AgentSettings,
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

    # @classmethod
    # def provision_agent(
    #     cls,
    #     agent_settings: AgentSettings,
    #     logger: logging.Logger,
    # ):
    #     agent_settings.agent.configuration.creation_time = datetime.now().strftime(
    #         "%Y%m%d_%H%M%S"
    #     )
    #     workspace: SimpleWorkspace = cls._get_system_instance(
    #         "workspace",
    #         agent_settings,
    #         logger=logger,
    #     )
    #     return workspace.create_workspace(agent_settings, logger)

    @classmethod
    def _get_system_instance(
        cls,
        system_name: str,
        agent_settings: dict,
        logger: logging.Logger,
        *args,
        **kwargs,
    ):
        system_locations = agent_settings.agent.configuration.systems.dict()

        system_settings = getattr(agent_settings, system_name)
        system_class = SimplePluginService.get_plugin(system_locations[system_name])
        system_instance = system_class(
            system_settings,
            *args,
            logger=logger.getChild(system_name),
            **kwargs,
        )
        return system_instance
    
    @classmethod
    def get_agentsetting_list_from_memory(self, user_id: uuid.UUID, logger: logging.Logger ) -> list[AgentSettings]:
        from autogpt.core.memory.base import Memory, MemoryAdapterType, MemoryConfig
        from autogpt.core.memory.table.base import AgentsTable, BaseTable
        """Warning !!!
        Returns a list of agent settings not a list of agent

        Returns:
            _type_: _description_
        """
        # TODO : Make config global
        config = MemoryConfig(
                memory_adapter=MemoryAdapterType.NOSQL_JSON_FILE,
                #json_file_path="~/auto-gpt/data/",
                json_file_path=str(Path("~/auto-gpt/data/").expanduser().resolve())
            )
        memory = Memory.get_adapter(config= config, logger=logger)
        agent_table : AgentsTable  =memory.get_table("agents")
       
        filter = BaseTable.FilterDict({
                                        "user_id" : 
                                       [BaseTable.FilterItem(value=str(user_id), operator= BaseTable.Operators.EQUAL_TO)]
                                       } 
                                       )
        agent_list = agent_table.list(filter = filter)
        return agent_list
   
    @classmethod
    def get_agent_from_memory(cls, agent_settings : AgentSettings, agent_id: uuid.UUID, user_id: uuid.UUID, logger: logging.Logger ) -> BaseAgent:
        from autogpt.core.memory.base import Memory, MemoryAdapterType, MemoryConfig
        from autogpt.core.memory.table.base import AgentsTable

        # TODO : Make config global
        config = MemoryConfig(
                memory_adapter=MemoryAdapterType.NOSQL_JSON_FILE,
                json_file_path=str(Path("~/auto-gpt/data/").expanduser().resolve())
            )
        memory = Memory.get_adapter(config= config, logger=logger)
        agent_table : AgentsTable  = memory.get_table("agents" )
        agent = agent_table.get(agent_id= str(agent_id), user_id=str(user_id))
        
        if not agent :
            return None
        agent = SimpleAgent.get_agent_from_settings(
            agent_settings=agent_settings,
            logger=logger,
        )
        return agent

def _prune_empty_dicts(d: dict) -> dict:
    """
    Prune branches from a nested dictionary if the branch only contains empty dictionaries at the leaves.

    Args:
        d: The dictionary to prune.

    Returns:
        The pruned dictionary.
    """
    pruned = {}
    for key, value in d.items():
        if isinstance(value, dict):
            pruned_value = _prune_empty_dicts(value)
            if (
                pruned_value
            ):  # if the pruned dictionary is not empty, add it to the result
                pruned[key] = pruned_value
        else:
            pruned[key] = value
    return pruned
