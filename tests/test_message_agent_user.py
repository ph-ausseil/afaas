import pytest
from unittest.mock import AsyncMock, MagicMock
from AFAAS.interfaces.agent.main import BaseAgent
from AFAAS.lib.message_common import AFAASMessage, AFAASMessageStack
from AFAAS.lib.message_agent_user import MessageAgentUser, Questions, Emiter 
from tests.dataset.plan_familly_dinner import (
    Task,
    plan_familly_dinner,
    plan_step_0,
    task_ready_no_predecessors_or_subtasks,
    default_task
)



# Test Instance Creation
@pytest.mark.asyncio
async def test_message_agent_user_creation():
    message_agent_user = MessageAgentUser(
        emitter=Emiter.USER.value,
        user_id="user123",
        agent_id="agent123",
        message="Sample message"
    )
    assert message_agent_user.emitter == Emiter.USER.value
    assert message_agent_user.user_id == "user123"
    assert message_agent_user.agent_id == "agent123"
    assert message_agent_user.message == "Sample message"
    assert isinstance(message_agent_user.message_id, str)

# Test UUID Generation
@pytest.mark.asyncio
async def test_uuid_generation():
    id1 = MessageAgentUser.generate_uuid()
    id2 = MessageAgentUser.generate_uuid()
    assert id1.startswith("MAU")
    assert id2.startswith("MAU")
    assert id1 != id2

# Test Load Method
@pytest.mark.asyncio
async def test_load_method():
    mock_agent = MagicMock(spec=BaseAgent)
    mock_agent.agent_id = "agent123"
    mock_table = MagicMock()
    mock_agent.db.get_table.return_value = mock_table
    mock_table.list.return_value = AsyncMock(return_value=[AFAASMessage()])

    result = await MessageAgentUser.load(mock_agent)
    assert isinstance(result, list)
    mock_table.list.assert_called_once()


@pytest.mark.asyncio
async def test_load_method_integration(default_task : Task):
    # Create a mock agent with a specific agent_id
    mock_agent = BaseAgent(agent_id="agent123")

    agent = default_task.agent
    message1 = MessageAgentUser(
        emitter=Emiter.USER,
        user_id= agent.user_id,
        agent_id=agent.agent_id,
        message="Sample message 1"
    )
    message2 = MessageAgentUser(
        emitter=Emiter.AGENT,
        user_id=agent.user_id,
        agent_id=agent.agent_id,
        message="Sample message 2"
    )

    agent.message_agent_user = AFAASMessageStack(db=agent.db) 
    await agent.message_agent_user.db_create(message=message1)
    await agent.message_agent_user.db_create(message=message2)

    # Now call the load method
    loaded_messages = await MessageAgentUser.load(mock_agent)

    # Validate that the loaded messages match what was inserted
    assert len(loaded_messages) == 2
    assert any(message.message == "Sample message 1" for message in loaded_messages)
    assert any(message.message == "Sample message 2" for message in loaded_messages)