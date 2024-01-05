"""Tools to interact with the user"""

from __future__ import annotations

TOOL_CATEGORY = "framework"
TOOL_CATEGORY_TITLE = "Framework"

# from AFAAS.lib.app import clean_input
from AFAAS.core.tools.tool_decorator import tool
from AFAAS.interfaces.agent.main import BaseAgent
from AFAAS.lib.task.task import Task
from AFAAS.lib.utils.json_schema import JSONSchema
from AFAAS.lib.message_agent_user import MessageAgentUser, emiter
from AFAAS.lib.message_common import AFAASMessageStack


@tool(
    "user_interaction",
    (
        "If you need more details or information regarding the given goals,"
        " you can ask the user for input"
    ),
    {
        "question": JSONSchema(
            type=JSONSchema.Type.STRING,
            description="The question or prompt to the user",
            required=True,
        )
    },
    enabled=lambda config: not config.noninteractive_mode,
)
async def user_interaction(question: str, task: Task, agent: BaseAgent) -> str:

    if False : # TODO : MAke user-proxy here
        pass

    if False and True : # If the user proxy found an answer
            return await agent._user_input_handler(question)


    agent.message_agent_user.add(
        message=MessageAgentUser(
            emitter=emiter.AGENT.value,
            user_id=agent.user_id,
            agent_id=agent.agent_id,
            message=question,
        )
    )
    user_response = await agent._user_input_handler(question)
    agent.message_agent_user.add(
            message=MessageAgentUser(
                emitter=emiter.USER.value,
                user_id=agent.user_id,
                agent_id=agent.agent_id,
                message=user_response,
            )
       )
    return user_response
