from __future__ import annotations

from typing import TYPE_CHECKING

from autogpt.core.ability import AbilityRegistrySettings
from autogpt.core.agent.base import *
from autogpt.core.planning import PlannerSettings
from autogpt.core.plugin.simple import PluginLocation
from autogpt.core.resource.model_providers import OpenAISettings

if TYPE_CHECKING:
    pass


class SimpleAgentSystems(BaseAgentSystems):
    ability_registry: PluginLocation
    openai_provider: PluginLocation
    planning: PluginLocation


class SimpleAgentConfiguration(BaseAgentConfiguration):
    systems: SimpleAgentSystems


class SimpleAgentSystemSettings(BaseAgentSystemSettings):
    configuration: SimpleAgentConfiguration


class SimpleAgentSettings(BaseAgentSettings):
    openai_provider: OpenAISettings
    ability_registry: AbilityRegistrySettings
    planning: PlannerSettings

    def update_agent_name_and_goals(self, agent_goals: dict) -> None:
        self.agent.configuration.name = agent_goals["agent_name"]
        self.agent.configuration.role = agent_goals["agent_role"]
        self.agent.configuration.goals = agent_goals["agent_goals"]
