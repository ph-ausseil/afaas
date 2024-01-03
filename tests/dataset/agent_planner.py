from __future__ import annotations

import uuid

from AFAAS.core.agents.planner.main import PlannerAgent
from AFAAS.lib.sdk.logger import AFAASLogger

LOG = AFAASLogger(name=__name__)

user_id= 'pytest_U3ba0a1c6-8cdf-4daa-a244-297b2057146a'

agent_settings: PlannerAgent.SystemSettings = PlannerAgent.SystemSettings(
    user_id=user_id,
    agent_id= 'A639f7cda-c88c-44d7-b0b2-a4a4abbd4a6c' ,
    agent_goal_sentence = 'Prepare a family dinner',
)

PLANNERAGENT = PlannerAgent(settings=agent_settings,
                             **agent_settings.dict()
                             )
