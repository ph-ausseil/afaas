"""Tools to control the internal state of the program"""

from __future__ import annotations

TOOL_CATEGORY = "framework"
TOOL_CATEGORY_TITLE = "Framework"

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from autogpt.core.agents.base import BaseAgent

from autogpt.core.agents.base.features.context import get_agent_context
from autogpt.core.utils.exceptions import InvalidArgumentError
from autogpt.core.tools.command_decorator import tool
from autogpt.core.utils.json_schema import JSONSchema
from autogpt.core.agents.whichway import (
    RoutingAgent,
    RoutingAgentSettings,
    )

logger = logging.getLogger(__name__)


@tool(
    name = "afaas_whichway",
    description = "Assist user refining it's requirements thus improving LLM responses",
    #parameters = ,
    hide = True
)
async def afaas_whichway(agent: BaseAgent) -> None:
    """
    Tool that help an agent to decide what kind of planning / execution to undertake
    """
    try : 
        # USER CONTEXT AGENT : Create Agent Settings
        usercontext_settings: RoutingAgentSettings = RoutingAgentSettings()
        usercontext_settings.user_id= agent.user_id
        usercontext_settings.parent_agent_id=  agent.agent_id
        usercontext_settings.agent_goals=  agent.agent_goals
        usercontext_settings.agent_goal_sentence=  agent.agent_goal_sentence
        usercontext_settings.memory  =  agent._memory._settings
        usercontext_settings.workspace =  agent._workspace._settings
        usercontext_settings.chat_model_provider=  agent._chat_model_provider._settings


        # USER CONTEXT AGENT : Save RoutingAgent Settings in DB (for POW / POC)
        new_user_context_agent = RoutingAgent.create_agent(
            agent_settings=usercontext_settings, logger=agent._logger
            )

        # # USER CONTEXT AGENT : Get RoutingAgent from DB (for POW / POC)
        usercontext_settings.agent_id = new_user_context_agent.agent_id

        user_context_agent = RoutingAgent.get_agent_from_settings(
            agent_settings=usercontext_settings,
            logger=agent._logger,
        )

        user_context_return: dict = await user_context_agent.run(
            user_input_handler = agent._user_input_handler,
            user_message_handler = agent._user_message_handler,
        )

        agent.agent_goal_sentence =     user_context_return["agent_goal_sentence"]
        agent.agent_goals =     user_context_return["agent_goals"]
    except Exception as e:
        raise str(e)
