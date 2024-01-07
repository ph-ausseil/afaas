import pytest
import os
from unittest.mock import AsyncMock, MagicMock
from AFAAS.lib.utils.json_schema import JSONSchema

# Assuming the not_implemented_tool function is defined in a module named `tools`
from AFAAS.core.tools.builtins.not_implemented_tool import not_implemented_tool
from AFAAS.core.tools.tool_decorator import tool
from AFAAS.interfaces.agent.main import BaseAgent
from tests.dataset.plan_familly_dinner import (
    Task,
    plan_familly_dinner,
    plan_step_0,
    task_ready_no_predecessors_or_subtasks,
)

@pytest.mark.asyncio
async def test_not_implemented_tool_basic():
    # Mock Task and BaseAgent
    mock_task = MagicMock()
    mock_agent = MagicMock()

    # Mock user_interaction to return a string
    mock_agent.user_interaction = AsyncMock(return_value="User Interaction Result")

    # Call the function with mocked objects and a test query
    result = await not_implemented_tool(task = mock_task, agent = mock_agent, query="Test Query")

    # Assert that the result is what user_interaction returns
    assert result == "User Interaction Result"
    mock_agent.user_interaction.assert_called_once_with(question="Test Query\n", task=mock_task, agent=mock_agent)


# Use a fixture to determine whether to run integration tests
@pytest.fixture(scope="session")
def activate_integration_tests():
    return os.getenv("RUN_INTEGRATION_TESTS", "false").lower() == "true"




@pytest.mark.asyncio
async def test_async_tool_not_implemented():
    @tool(name="async_test_tool", description="Async Test Tool")
    async def async_test_tool(agent: BaseAgent, task : Task) -> str:
        raise NotImplementedError

    mock_agent = MagicMock()
    mock_task = MagicMock()
    mock_agent.user_interaction = AsyncMock(return_value="Async Tool Fallback")

    result = await async_test_tool(task = mock_task, agent = mock_agent)
    assert result == "Async Tool Fallback"



def test_sync_tool_not_implemented():
    @tool(name="sync_test_tool", description="Sync Test Tool")
    def sync_test_tool(agent: BaseAgent, task : Task) -> str:
        raise NotImplementedError

    mock_agent = MagicMock()
    mock_task = MagicMock()
    mock_agent.user_interaction = MagicMock(return_value="Sync Tool Fallback")

    result = sync_test_tool(task = mock_task, agent = mock_agent)
    assert result == "Sync Tool Fallback"

@pytest.mark.asyncio
async def test_async_tool_with_args_not_implemented():
    @tool(
        name="async_test_tool_args",
        description="Async Test Tool with Args",
        parameters={"query": JSONSchema(type=JSONSchema.Type.STRING, required=True)}
    )
    async def async_test_tool_args(query: str, agent: BaseAgent, task : Task) -> str:
        raise NotImplementedError

    mock_agent = MagicMock()
    mock_task = MagicMock()
    mock_agent.user_interaction = AsyncMock(return_value="Async Tool Args Fallback")

    result = await async_test_tool_args(query="Test Query", task = mock_task, agent = mock_agent)
    assert result == "Async Tool Args Fallback"




@pytest.mark.asyncio
async def test_async_tool_no_kwargs_not_implemented():
    @tool(name="async_test_tool_no_kwargs", description="Async Test Tool No KWArgs")
    async def async_test_tool_no_kwargs(agent: BaseAgent, task : Task) -> str:
        raise NotImplementedError

    mock_agent = MagicMock()
    mock_task = MagicMock()
    mock_agent.user_interaction = AsyncMock(return_value="Async Tool No KWArgs Fallback")

    result = await async_test_tool_no_kwargs(task = mock_task, agent = mock_agent)
    assert result == "Async Tool No KWArgs Fallback"


@pytest.mark.asyncio
async def test_not_implemented_tool_integration(activate_integration_tests, task_ready_no_predecessors_or_subtasks):
    if not activate_integration_tests:
        pytest.skip("Integration tests are not activated")

    # Here, you would set up real or semi-real Task and BaseAgent
    real_task = task_ready_no_predecessors_or_subtasks
    real_agent = task_ready_no_predecessors_or_subtasks.agent

    # Call the function with real or semi-real objects
    result = await not_implemented_tool(task = real_task, agent = real_agent, query="Integration Test Query")

    #FIXME: Maxe assetions
    pytest.skip("Not Implemented Tool Integration Test Assertions Not Implemented")

