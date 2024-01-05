from __future__ import annotations

TOOL_CATEGORY = "framework"
TOOL_CATEGORY_TITLE = "Framework"

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from AFAAS.interfaces.agent.main import BaseAgent

from AFAAS.core.tools.tool_decorator import tool
from AFAAS.lib.sdk.logger import AFAASLogger
from AFAAS.lib.task.task import Task
from AFAAS.lib.utils.json_schema import JSONSchema
from AFAAS.interfaces.prompts.strategy import AbstractChatModelResponse
from AFAAS.core.tools.builtins.user_interaction import user_interaction
from AFAAS.core.tools.untested.query_language_model import query_language_model
LOG = AFAASLogger(name=__name__)


@tool(
    name="search_info",
    description=(
        "Find a publicly available information, will find information availale on the web, if fails the user will provide you with the information you seek."
    ),
    parameters={
        "query": JSONSchema(
            type=JSONSchema.Type.STRING,
            description="A query for a language model. A query should contain a question and any relevant context.",
            required=True,
        )
    },
)
async def search_info(query : str, task: Task, agent: BaseAgent) -> None:

    search_result: AbstractChatModelResponse = await agent.execute_strategy(
        strategy_name="search_info", agent=agent, task=task, query=query
    )

    command_name = search_result.parsed_result[0]
    command_args = search_result.parsed_result[1]
    assistant_reply_dict = search_result.parsed_result[2]

    if command_name == "query_language_model":
        return await query_language_model(task = task, agent = agent, **command_args)
    elif command_name == "user_interaction" :
        return await user_interaction(task = task, agent = agent, **command_args)
    elif command_name == "web_search" :
        try : 
            from AFAAS.core.tools.untested.web_search import web_search
            web_search(task = task, agent = agent, **command_args)
        except :
            raise NotImplementedError("Command search_web not implemented")
    else :
        raise NotImplementedError(f"Command {command_name} not implemented")

