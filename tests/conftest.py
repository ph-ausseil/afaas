import uuid
from pathlib import Path

import pytest
from AFAAS.core.agents.planner.main import PlannerAgent
from AFAAS.core.workspace import AbstractFileWorkspace
from AFAAS.interfaces.tools.base import BaseToolsRegistry


def agent_dataset(
) -> PlannerAgent:
    PlannerAgentSettings = PlannerAgent.SystemSettings(
        user_id= 'pytest_U3ba0a1c6-8cdf-4daa-a244-297b2057146a' ,
        agent_id= 'A639f7cda-c88c-44d7-b0b2-a4a4abbd4a6c' ,
        agent_goal_sentence = 'Prepare a family dinner',
    )
    agent = PlannerAgent(
        settings= PlannerAgentSettings,
        **PlannerAgentSettings.dict()
    )
    return agent

@pytest.fixture
def agent() -> PlannerAgent:
    return agent_dataset()

@pytest.fixture
def local_workspace(
) -> AbstractFileWorkspace : 
    return agent_dataset().workspace

@pytest.fixture
def empty_tool_registry() -> BaseToolsRegistry:
    registry = agent_dataset().tool_registry
    registry.tools = {}
    return registry
