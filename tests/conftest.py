
from pathlib import Path

import pytest
from AFAAS.core.agents.planner.main import PlannerAgent
from AFAAS.core.workspace import AbstractFileWorkspace

@pytest.fixture
def agent(
) -> PlannerAgent:
    return PlannerAgent(
    )

@pytest.fixture
def local_workspace(
) -> AbstractFileWorkspace : 
    return agent().workspace
