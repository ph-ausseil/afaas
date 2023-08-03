from __future__ import annotations

import abc
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Awaitable, Callable, List

if TYPE_CHECKING:
    from autogpt.core.agent.base.loop import (  # Import only where it's needed
        BaseLoop,
        BaseLoopHook,
    )

from autogpt.core.ability import AbilityRegistry
from autogpt.core.agent.base.models import (
    BaseAgentConfiguration,
    BaseAgentSettings,
    BaseAgentSystems,
    BaseAgentSystemSettings,
)
from autogpt.core.configuration import Configurable
from autogpt.core.memory import Memory
from autogpt.core.plugin.simple import SimplePluginService
from autogpt.core.workspace import Workspace


class AgentConfigurable(Configurable):
    pass


class BaseAgent(abc.ABC):
    AGENT_SYSTEM_SETINGS = BaseAgentSystemSettings
    AGENT_CONFIGURATION = BaseAgentConfiguration
    AGENT_SETTINGS = BaseAgentSettings
    AGENT_SYSTEMS = BaseAgentSystems

    @classmethod
    def get_agent_class(cls) -> Agent:
        print(cls)
        return cls

    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        ...

    @classmethod
    @abc.abstractmethod
    def from_workspace(
        cls, workspace_path: Path, logger: logging.Logger
    ) -> "BaseAgent":
        ...

    @abc.abstractmethod
    def __repr__(self):
        ...


class Agent(BaseAgent):
    def __call__(
        self,
        settings: BaseAgentSystemSettings,
        logger: logging.Logger,
        ability_registry: AbilityRegistry,
        memory: Memory,
        workspace: Workspace,
    ) -> Any:
        print("BEGIN CALL : Agent.__call.__ : self.__class__\n")
        print(self.__class__)
        self._configuration = settings.configuration
        self._logger = logger
        self._ability_registry = ability_registry
        self._memory = memory
        # FIXME: Need some work to make this work as a dict of providers
        #  Getting the construction of the config to work is a bit tricky
        self._workspace = workspace
        self._task_queue = []
        self._completed_tasks = []
        self._current_task = None
        self._next_ability = None
        self._isrunning = True

        print("END CALL : Agent.__call.__ : self\n")
        print(self)
        return super().__call__(
            self, settings, logger, ability_registry, memory, workspace
        )

    @property
    @abc.abstractmethod
    def _loophooks(self) -> List[BaseLoop.LoophooksDict]:
        pass

    @property
    @abc.abstractmethod
    def loop(self) -> BaseLoop:
        pass

    # @property
    # @abc.abstractmethod
    # def default_callback(self, hook_name: str, result: Any) -> None:
    #     pass

    # @property
    # @abc.abstractmethod
    # def default_callback(self) -> dict[str, Callable[[Any, Any, Any], Any]]:
    #     pass

    def add_hook(self, name: str, hook: BaseLoopHook, uuid: uuid.UUID):
        self._loophooks[name][uuid] = hook

    def remove_hook(self, name: str, uuid: uuid.UUID) -> bool:
        if uuid in self._loophooks[name].keys():
            self._loophooks[name][uuid].remove()
            return True
        return False

    async def start(
        self,
        agent: Agent,
        user_input_handler: Callable[[str], Awaitable[str]],
        user_message_handler: Callable[[str], Awaitable[str]],
    ) -> None:
        return_var = await self._loop.start(
            agent=self,
            user_input_handler=user_input_handler,
            user_message_handler=user_message_handler,
        )
        return return_var

    async def stop(
        self,
        agent: Agent,
        user_input_handler: Callable[[str], Awaitable[str]],
        user_message_handler: Callable[[str], Awaitable[str]],
    ) -> None:
        return_var = await self._loop.stop(
            agent=self,
            user_input_handler=user_input_handler,
            user_message_handler=user_message_handler,
        )
        return return_var

    async def run(
        self,
        user_input_handler: Callable[[str], Awaitable[str]],
        user_message_handler: Callable[[str], Awaitable[str]],
        *kwargs,
    ) -> None:
        print("BaseAgent.run() *kwarg : " + str(kwargs))
        if not self.loop.isrunning:
            self.loop.isrunning = True
            self.loop.run(
                agent=self,
                hooks=self._loophooks,
                user_input_handler=user_input_handler,
                user_message_handler=user_message_handler,
                *kwargs,
            )
        else:
            raise BaseException("Agent Already Running")

    def exit(self, *kwargs) -> None:
        if self.loop.isrunning:
            self.loop.isrunning = False

    @classmethod
    @abc.abstractmethod
    def from_workspace(
        cls,
        workspace_path: Path,
        logger: logging.Logger,
    ) -> Agent:
        # if TYPE_CHECKING:
        from autogpt.core.workspace import SimpleWorkspace

        agent_settings = SimpleWorkspace.load_agent_settings(cls, workspace_path)
        agent_args = {}

        agent_args["settings"] = agent_settings.agent
        agent_args["logger"] = logger
        agent_args["workspace"] = cls._get_system_instance(
            "workspace",
            agent_settings,
            logger,
        )
        agent_args["memory"] = cls._get_system_instance(
            "memory",
            agent_settings,
            logger,
            workspace=agent_args["workspace"],
        )

        return agent_settings, agent_args

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
        cls: Agent, logger: logging.Logger, user_configuration: dict
    ) -> BaseAgentSettings:
        """Compile the user's configuration with the defaults."""
        logger.debug("Processing agent system configuration.")
        print("compile_settings" + str(cls))
        configuration_dict = {
            "agent": cls.build_agent_configuration(
                user_configuration.get("agent", {})
            ).dict(),
        }

        system_locations = configuration_dict["agent"]["configuration"]["systems"]

        # Build up default configuration
        for system_name, system_location in system_locations.items():
            logger.debug(f"Compiling configuration for system {system_name}")
            system_class = SimplePluginService.get_plugin(system_location)
            configuration_dict[system_name] = system_class.build_agent_configuration(
                user_configuration.get(system_name, {})
            ).dict()

        return cls.AGENT_SETTINGS.parse_obj(configuration_dict)

    ################################################################
    # Factory interface for agent bootstrapping and initialization #
    ################################################################

    def check_user_context(self, min_len=250, max_len=300):
        pass

    @classmethod
    def provision_agent(
        cls,
        agent_settings: BaseAgentSettings,
        logger: logging.Logger,
    ):
        agent_settings.agent.configuration.creation_time = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        # TODO : Setup up Memory not workspace
        from autogpt.core.workspace import SimpleWorkspace

        workspace: SimpleWorkspace = cls._get_system_instance(
            "workspace",
            agent_settings,
            logger=logger,
        )
        return workspace.setup_workspace(agent_settings, logger)

    @classmethod
    def create_agent_in_memory(
        cls,
        agent_settings: BaseAgentSettings,
        logger: logging.Logger,
    ):
        agent_settings.agent.configuration.creation_time = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        from autogpt.core.memory.base import NewMemory

        memory = NewMemory.get_adapter(memory_adapter="json_file", logger=logger)
        agent_id = memory.get_table("agents").add(agent_settings)
        return agent_id

    @classmethod
    def provision_agent_from_memory(
        cls,
        agent_settings: BaseAgentSettings,
        logger: logging.Logger,
    ):
        """DEPRECATED : Alias of create_agent_in_memory

        Args:
            agent_settings (BaseAgentSettings): _description_
            logger (logging.Logger): _description_
        """
        cls.create_agent_in_memory(agent_settings, logger)

    @classmethod
    def _get_system_instance(
        cls,
        system_name: str,
        agent_settings: BaseAgentSettings,
        logger: logging.Logger,
        *args,
        **kwargs,
    ):
        print("\ncls._get_system_instance : " + str(cls))
        print("\n_get_system_instance agent_settings: " + str(agent_settings))
        print("\n_get_system_instance system_name: " + str(system_name))
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
