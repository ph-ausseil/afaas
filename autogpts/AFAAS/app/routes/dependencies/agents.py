
from fastapi import APIRouter, Query, Request, Response, UploadFile, Depends

from app.sdk.errors import *
from app.sdk.forge_log import ForgeLogger
from app.sdk.schema import *

LOG = ForgeLogger(__name__)
from fastapi import APIRouter, FastAPI, Request

from autogpts.autogpt.autogpt.core.agents import PlannerAgent


            
def get_agent(request: Request, agent_id: str) -> PlannerAgent:
    agent : PlannerAgent = PlannerAgent.get_agent_from_memory(
        agent_id=agent_id,
        user_id=request.state.user_id,
        logger=LOG,
        )
    if agent is None : 
        raise NotFoundError
    else : 
        return agent