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

LOG = AFAASLogger(name=__name__)


@tool(
    name="query_language_model",
    description=(
        "Search the web and with the capacity of returning steerable & structured result. Not very good at retriving data published last month."
    ),
    parameters={
        "query": JSONSchema(
            type=JSONSchema.Type.STRING,
            description="A query for a language model. A query should contain a question and any relevant context.",
            required=True,
        ),
        "format": JSONSchema(
            type=JSONSchema.Type.STRING,
            description="Describe the format (plan, length,...) of the expected answer.",
            required=True,
        ),
        "answer_as": JSONSchema(
            type=JSONSchema.Type.STRING,
            description="Describe the ideal persona persona with his profession, expertise, mindset, personnality, ect... You would like to get an answer from.",
            required=True,
        ),
        "example": JSONSchema(
            type=JSONSchema.Type.STRING,
            description="As large language model, this tool will give much  better results if given example of phrasing, format, ext you may expept.",
        ),
    },
)
async def query_language_model(task: Task, agent: BaseAgent) -> None:

    plan = await agent.execute_strategy(
        strategy_name="query_llm", agent=agent, task=task
    )

    return plan
