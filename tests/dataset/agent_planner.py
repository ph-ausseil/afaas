from __future__ import annotations

import uuid

from AFAAS.core.agents.planner.main import PlannerAgent
from AFAAS.interfaces.db.db import AbstractMemory, MemoryAdapterType, MemoryConfig
from AFAAS.lib.message_common import AFAASMessage, AFAASMessageStack
from AFAAS.lib.sdk.logger import AFAASLogger
from AFAAS.lib.sdk.user_message_handlers import UserMessageHandlers

LOG = AFAASLogger(name=__name__)

# user_id = "pytest_U3ba0a1c6-8cdf-4daa-a244-297b2057146a"

# agent_settings: PlannerAgent.SystemSettings = PlannerAgent.SystemSettings(
#     user_id=user_id,
#     agent_id="pytest_A639f7cda-c88c-44d7-b0b2-a4a4abbd4a6c" + str(uuid.uuid4()),
#     agent_goal_sentence="Prepare a family dinner",
# )

# db_config = MemoryConfig()
# db_config.json_file_path += "/pytest"
# db_settings = AbstractMemory.SystemSettings()
# db_settings.configuration = db_config

# agent = PlannerAgent(
#     settings=agent_settings,
#     **agent_settings.model_dump(),
#     db=AbstractMemory.get_adapter(settings=db_settings),
# )

# PLANNERAGENT = agent


# import sys
# from pathlib import Path

# # Get the parent directory of the current file (conftest.py)
# parent_dir = Path(__file__).parent
# sys.path.append(str(parent_dir))


async def agent_dataset(
    user_id="pytest_U3ba0a1c6-8cdf-4daa-a244-297b2057146a",
    agent_id="pytest_A639f7cda-c88c-44d7-b0b2-a4a4abbd4a6c",
) -> PlannerAgent:
    import uuid

    # user_id = "pytest_USE" + str(uuid.uuid4())
    # agent_id = "pytest_AGE" + str(uuid.uuid4())
    from AFAAS.core.agents.planner.main import PlannerAgent
    from AFAAS.interfaces.db.db import AbstractMemory, MemoryAdapterType, MemoryConfig
    from AFAAS.lib.sdk.logger import AFAASLogger

    LOG = AFAASLogger(name=__name__)

    agent_settings: PlannerAgent.SystemSettings = PlannerAgent.SystemSettings(
        user_id=user_id,
        agent_id=agent_id,
        agent_goal_sentence="Prepare a family dinner",
    )

    # #FIXME :
    # #agent = PlannerAgent(settings=agent_settings, **agent_settings.model_dump())
    # db_config = MemoryConfig()
    # db_config.json_file_path += "/pytest"
    # db_settings = AbstractMemory.SystemSettings()
    # db_settings.configuration = db_config
    # db = AbstractMemory.get_adapter(settings=db_settings)

    # agent = await PlannerAgent.load(
    #     settings=agent_settings,
    #     **agent_settings.model_dump(),
    #     db=db ,
    # )
    # #NOTE:Hack
    # #agent.db._settings.configuration.json_file_path += "/pytest"
    agent = PlannerAgent(settings=agent_settings, **agent_settings.model_dump())

    agent.message_agent_user = AFAASMessageStack(db=agent.db)
    agent._user_input_handler = UserMessageHandlers.user_input_handler
    agent._user_message_handler = UserMessageHandlers.user_message_handler
    await agent.db_create()
    return agent
