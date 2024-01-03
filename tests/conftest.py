
import pytest
from AFAAS.core.agents.planner.main import PlannerAgent
from AFAAS.core.workspace import AbstractFileWorkspace
from AFAAS.interfaces.tools.base import BaseToolsRegistry
from tests.dataset.agent_planner import agent_dataset

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
