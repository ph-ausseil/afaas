from __future__ import annotations

import abc
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from autogpt.core.ability import AbilityRegistrySettings
from autogpt.core.configuration import SystemConfiguration, SystemSettings
from autogpt.core.memory.base import MemorySettings
from autogpt.core.planning import PlannerSettings
from autogpt.core.plugin.simple import PluginLocation
from autogpt.core.resource.model_providers import OpenAISettings
from autogpt.core.workspace.simple import WorkspaceSettings


class Agent(abc.ABC):
    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        ...

    @classmethod
    @abc.abstractmethod
    def get_agent_from_settings(
        cls,
        workspace_path: Path,
        logger: logging.Logger,
    ) -> "Agent":
        ...

    @abc.abstractmethod
    async def determine_next_ability(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    def __repr__(self):
        ...


class AgentSystems(SystemConfiguration):
    ability_registry: PluginLocation
    memory: PluginLocation
    openai_provider: PluginLocation
    planning: PluginLocation
    workspace: PluginLocation
    user_id: Optional[uuid.UUID] = Field(default=None)
    agent_id: Optional[uuid.UUID] = Field(default=None)

class AgentConfiguration(SystemConfiguration):
    cycle_count: int
    max_task_cycle_count: int
    creation_time: str
    systems: AgentSystems
    user_id: Optional[uuid.UUID] = Field(default=None)
    agent_id: Optional[uuid.UUID] = Field(default=None)
    agent_name: str = Field(default='New Agent')
    agent_role: Optional[str] = Field(default=None)
    agent_goals: Optional[list[str]] = Field(default=None)



class AgentSystemSettings(SystemSettings):
    configuration: AgentConfiguration
    user_id: Optional[uuid.UUID] = Field(default=None)
    agent_id: Optional[uuid.UUID] = Field(default=None)


class AgentSettings(BaseModel):
    agent: AgentSystemSettings
    ability_registry: AbilityRegistrySettings
    memory: MemorySettings
    openai_provider: OpenAISettings
    planning: PlannerSettings
    workspace: WorkspaceSettings
    user_id: Optional[uuid.UUID] = Field(default=None)
    agent_id: Optional[uuid.UUID] = Field(default=None)
    agent_name: str = Field(default='New Agent')
    agent_role: Optional[str] = Field(default=None)
    agent_goals: Optional[list] = Field(default=None)

    class Config:
         # This is a list of Field to Exclude during serialization
        json_encoders = {
            uuid.UUID: lambda v: str(v)  # Custom encoder for UUID4
        }
        default_exclude = {"workspace", "planning", "openai_provider", "memory", "ability_registry"}
            

    def dict(self, remove_technical_values=True, *args, **kwargs):
        self.prepare_values_before_serialization()  # Call the custom treatment before .dict()

        kwargs['exclude'] = kwargs.get('exclude', set())  # Get the exclude_arg
        if remove_technical_values:
            # Add the default technical fields to exclude_arg
            kwargs['exclude'] |= self.__class__.Config.default_exclude

        # Call the .dict() method with the updated exclude_arg
        return super().dict( *args, **kwargs)
       

    def json(self, *args, **kwargs):
        self.prepare_values_before_serialization()  # Call the custom treatment before .json()
        return super().json(*args, **kwargs)


    def update_agent_name_and_goals(self, agent_goals: dict) -> None:
        self.agent.configuration.agent_name = agent_goals["agent_name"]
        self.agent.configuration.agent_role = agent_goals["agent_role"]
        self.agent.configuration.agent_goals = agent_goals["agent_goals"]

        self.agent_name = 'New'+ agent_goals["agent_name"]
        self.agent_role = 'New'+ agent_goals["agent_role"]
        self.agent_goals = agent_goals["agent_goals"]

   
    
        
    # NOTE : To be implemented in the future
    def load_root_values(self, *args, **kwargs):
        self.agent_name = self.agent.configuration.agent_name
        self.agent_role = self.agent.configuration.agent_role
        self.agent_goals = self.agent.configuration.agent_goals
    
    def prepare_values_before_serialization(self):
        self.agent_name = self.agent.configuration.agent_name
        self.agent_role = self.agent.configuration.agent_role
        self.agent_goals = self.agent.configuration.agent_goals
    
class BaseAgent(Agent):

    @classmethod
    def create_agent_in_memory(
        cls, agent_settings: AgentSettings, logger: logging.Logger, user_id : uuid.UUID
    ) -> uuid.UUID:
        agent_settings.agent.configuration.creation_time = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )        
        # TODO : Remove the user_id argument
        # NOTE : Monkey Patching
        AgentSettings.Config.extra = "allow"
        SystemSettings.Config.extra = "allow"   
        AgentSystems.Config.extra = "allow" 
        AgentConfiguration.Config.extra = "allow"
        agent_settings.agent.configuration.user_id = str(user_id)
        AgentSystems.user_id: uuid.UUID
        agent_settings.user_id= str(user_id)

        from autogpt.core.memory.base import Memory, MemoryAdapterType, MemoryConfig
        config = MemoryConfig(
                memory_adapter=MemoryAdapterType.NOSQL_JSON_FILE,
                #json_file_path="~/auto-gpt/data/",
                json_file_path=str(Path("~/auto-gpt/data/").expanduser().resolve())
            )
        memory = Memory.get_adapter(config= config, logger=logger)
        agent_table = memory.get_table("agents")
        agent_id = agent_table.add(agent_settings)
        return agent_id
