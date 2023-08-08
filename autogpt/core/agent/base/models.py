from pydantic import BaseModel

from autogpt.core.configuration import SystemConfiguration, SystemSettings
from autogpt.core.memory import MemorySettings
from autogpt.core.plugin.simple import PluginLocation
from autogpt.core.workspace.simple import WorkspaceSettings


class BaseAgentSystems(SystemConfiguration):
    memory: PluginLocation
    workspace: PluginLocation

    class Config:
        extra = "allow"


class BaseAgentConfiguration(SystemConfiguration):
    cycle_count: int
    max_task_cycle_count: int
    creation_time: str
    name: str
    role: str
    goals: list[str]
    systems: BaseAgentSystems


class BaseAgentSystemSettings(SystemSettings):
    configuration: BaseAgentConfiguration


class BaseAgentSettings(BaseModel):
    agent: BaseAgentSystemSettings
    memory: MemorySettings
    workspace: WorkspaceSettings

    # def update_agent_name_and_goals(self, agent_goals: dict) -> None:
    #     self.agent.configuration.name = agent_goals["agent_name"]
    #     self.agent.configuration.role = agent_goals["agent_role"]
    #     self.agent.configuration.goals = agent_goals["agent_goals"]
