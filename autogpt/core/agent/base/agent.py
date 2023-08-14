from __future__ import annotations

import abc
import logging
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Awaitable, Callable, List , Dict

if TYPE_CHECKING:
    from autogpt.core.agent.base.loop import (  # Import only where it's needed
        BaseLoop,
        BaseLoopHook,
    )

from autogpt.core.agent.base.loop import (  # Import only where it's needed
        BaseLoopHook,
    )

from autogpt.core.ability import AbilityRegistry
from autogpt.core.agent.base.models import (
    BaseAgentConfiguration,
    BaseAgentSettings,
    BaseAgentSystems,
    BaseAgentSystemSettings,
)
from autogpt.core.memory.base import Memory
from autogpt.core.plugin.simple import SimplePluginService
from autogpt.core.workspace import Workspace

class BaseAgent(abc.ABC):
    AGENT_SYSTEM_SETINGS = BaseAgentSystemSettings
    AGENT_CONFIGURATION = BaseAgentConfiguration
    AGENT_SETTINGS = BaseAgentSettings
    AGENT_SYSTEMS = BaseAgentSystems

    @classmethod
    def get_agent_class(cls) -> Agent:
        return cls

    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        ...

    @classmethod
    @abc.abstractmethod
    def get_agent_from_settings(
        cls,
        agent_settings: BaseAgentSettings,
        logger: logging.Logger,
    ) -> "BaseAgent":
        ...

    @abc.abstractmethod
    def __repr__(self):
        ...

    _loop : BaseLoop = None
    #_loophooks: Dict[str, BaseLoop.LoophooksDict] = {}

class Agent(BaseAgent):

    def __init__(
        self,
        settings: BaseAgentSystemSettings,
        logger: logging.Logger,
        ability_registry: AbilityRegistry,
        memory: Memory,
        workspace: Workspace,
        user_id: uuid.UUID,
        agent_id: uuid.UUID = None,
    ) -> Any:
        logger.info(f"Agent.__init__ : self.__class__ = {str(self.__class__)}\n")

        
        self._configuration = settings.configuration
        self._logger = logger
        self._ability_registry = ability_registry
        self._memory = memory
        self._workspace = workspace

        self.user_id = user_id
        self.agent_id = agent_id
        self.agent_type = self.__class__.__name__

        logger.debug(f"Agent.__init__ : self = {str(self)}\n")
        return super().__init__(
            self, settings, logger, ability_registry, memory, workspace
        )


    def add_hook(self, hook: BaseLoopHook, hook_id: uuid.UUID = uuid.uuid4()):
        self._loop._loophooks[hook['name']][str(hook_id)] = hook

    def remove_hook(self, name: str, hook_id: uuid.UUID) -> bool:
        if name in self._loop._loophooks and hook_id in self._loop._loophooks[name]:
            del self._loop._loophooks[name][hook_id]
            return True
        return False

    async def start(
        self,
        user_input_handler: Callable[[str], Awaitable[str]],
        user_message_handler: Callable[[str], Awaitable[str]],
    ) -> None:
        self._logger.info( str(self.__class__)+".start()")
        return_var = await self._loop.start(
            agent=self,
            user_input_handler=user_input_handler,
            user_message_handler=user_message_handler,
        )
        return return_var

    async def stop(
        self,
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
        **kwargs,
    ) -> None:
        
        self._logger.debug(str(self.__class__) + ".run() *kwarg : " + str(kwargs))

        if not self._loop._is_running:
            self._loop._is_running = True
            # Very important, start the loop :-)
            await self.start(
                user_input_handler=user_input_handler,
                user_message_handler=user_message_handler,
                )

            await self._loop.run(
                agent=self,
                hooks=self._loop._loophooks,
                user_input_handler=user_input_handler,
                user_message_handler=user_message_handler,
                #*kwargs,
            )

        else:
            raise BaseException("Agent Already Running")
        

    def exit(self, *kwargs) -> None:
        if self._loop._is_running:
            self._loop._is_running = False

    @classmethod
    @abc.abstractmethod
    def get_agent_from_settings(
        cls,
        agent_settings: BaseAgentSettings,
        logger: logging.Logger,
    ) -> Agent:

        if not isinstance(agent_settings, BaseAgentSettings):
            agent_settings: BaseAgentSettings = agent_settings
        agent_args = {}

        agent_args['user_id'] = agent_settings.user_id
        agent_args["settings"] = agent_settings.agent
        agent_args["logger"] = logger
        agent_args["workspace"] = cls._get_system_instance(
            "workspace",
            agent_settings,
            logger,
        )
        
        memory_settings = agent_settings.memory
        agent_args["memory"] =  Memory.get_adapter(memory_settings= memory_settings, logger=logger)

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
        cls, 
        logger: logging.Logger, 
        user_configuration: dict
    ) -> BaseAgentSettings:

        """Compile the user's configuration with the defaults."""
        logger.debug("Processing agent system configuration.")
        logger.debug("compile_settings" + str(cls))
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

        return cls.AGENT_SETTINGS.parse_obj(configuration_dict)

    ################################################################
    # Factory interface for agent bootstrapping and initialization #
    ################################################################

    def check_user_context(self, min_len=250, max_len=300):
        pass

    @classmethod
    def create_agent(cls,
        agent_settings: BaseAgentSettings,
        logger: logging.Logger,) -> uuid.UUID:
        """Create a new agent."""
        agent_id = cls.create_agent_in_memory(agent_settings=agent_settings, 
                                              logger=logger,
                                              user_id = agent_settings.user_id)
        agent_settings.agent.agent_id = agent_id
        agent_settings.agent_id = agent_id
        cls._create_workspace(agent_settings=agent_settings, logger=logger)
        return agent_id

    
    @classmethod
    def _create_workspace(
        cls,
        agent_settings: BaseAgentSettings,
        logger: logging.Logger,
    ):
        from autogpt.core.workspace import SimpleWorkspace
        return SimpleWorkspace.create_workspace(
            user_id=agent_settings.user_id, 
            agent_id=agent_settings.agent_id,  
            settings = agent_settings, 
            logger=logger)
    
    @classmethod
    def create_agent_in_memory(
        cls,
        agent_settings: BaseAgentSettings,
        logger: logging.Logger,
        user_id : uuid.UUID
    ) -> uuid.UUID:
        agent_settings.agent.configuration.creation_time = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )        
        # TODO : Remove the user_id argument
        # NOTE : Monkey Patching
        BaseAgentSettings.Config.extra = "allow"
        BaseAgentSystemSettings.Config.extra = "allow"   
        BaseAgentSystems.Config.extra = "allow" 
        BaseAgentConfiguration.Config.extra = "allow"
        agent_settings.agent.configuration.user_id = str(user_id)
        BaseAgentSystems.user_id: uuid.UUID
        agent_settings.user_id= str(user_id)

        from autogpt.core.memory.base import Memory
        memory_settings = agent_settings.memory

        memory = Memory.get_adapter(memory_settings= memory_settings, logger=logger)
        agent_table = memory.get_table("agents")
        agent_id = agent_table.add(agent_settings)
        return agent_id


    @classmethod
    def _get_system_instance(
        cls,
        system_name: str,
        agent_settings: BaseAgentSettings,
        logger: logging.Logger,
        *args,
        **kwargs,
    ):
        logger.debug("\ncls._get_system_instance : " + str(cls))
        logger.debug("\n_get_system_instance agent_settings: " + str(agent_settings))
        logger.debug("\n_get_system_instance system_name: " + str(system_name))
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

