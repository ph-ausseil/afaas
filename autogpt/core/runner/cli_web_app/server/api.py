import uuid
from pathlib import Path
import yaml
from fastapi import APIRouter, FastAPI, Request
from autogpt.core.runner.client_lib.shared_click_commands import (
    DEFAULT_SETTINGS_FILE,
    make_settings,
)
from autogpt.core.runner.cli_web_app.server.schema import InteractRequestBody
from autogpt.core.runner.cli_web_app.server.services.agent import workspace_loader

router = APIRouter()
def get_settings_from_file() : 
    """ 
    Current Back-end for setting is a File 
    """
    # @Todo : Possible Back-End No SQL Database 
    settings_file = Path(DEFAULT_SETTINGS_FILE)
    settings = {}
    if settings_file.exists():
        settings = yaml.safe_load(settings_file.read_text())
    return settings;


@router.get("/agents")
async def get_agents(request: Request):
    """List all agents"""
    settings = get_settings_from_file()
    agent = await workspace_loader(settings).__dict__
    # @Todo place holder for elements
    agent.agent_id = uuid.uuid4().hex
    agent.client_facing = True
    agent.status = 0
    return {"agents": [agent]}


@router.post("/agent")
async def create_agent(request: Request):
    """Create a new agent."""
    agent_id = uuid.uuid4().hex
    return {"agent_id": agent_id}


@router.get("/agent/{agent_id}")
async def get_agent_by_id(request: Request, agent_id: str, body: InteractRequestBody):
    agent = get_settings_from_file()
    return {"agent": }


@router.post("/agent/{agent_id}")
async def interact(request: Request, agent_id: str, body: InteractRequestBody):
    """Interact with an agent."""

    # check headers

    # check if agent_id exists

    # get agent object from somewhere, e.g. a database/disk/global dict

    # continue agent interaction with user input

    return {
        "thoughts": {
            "thoughts": {
                "text": "text",
                "reasoning": "reasoning",
                "plan": "plan",
                "criticism": "criticism",
                "speak": "speak",
            },
            "commands": {
                "name": "name",
                "args": {"arg_1": "value_1", "arg_2": "value_2"},
            },
        },
        "messages": ["message1", agent_id],
    }


app = FastAPI()
app.include_router(router, prefix="/api/v1")
