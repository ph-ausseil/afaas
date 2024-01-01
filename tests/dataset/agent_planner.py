from __future__ import annotations

import uuid

from AFAAS.core.agents.planner.main import PlannerAgent
from AFAAS.lib.sdk.logger import AFAASLogger

LOG = AFAASLogger(name=__name__)

user_id= 'pytest_U' + str(uuid.uuid4())

agent_settings: PlannerAgent.SystemSettings = PlannerAgent.SystemSettings(
    user_id=user_id,
    agent_goal_sentence = 'Prepare a family dinner',
)

PLANNERAGENT = PlannerAgent(settings=agent_settings,
                             **agent_settings.dict()
                             )
