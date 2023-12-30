import uuid

from AFAAS.configs.schema import AFAASMessageType
from AFAAS.lib.message_common import AFAASMessage


class MessageAgentAgent(AFAASMessage):
    message_id: str = "MAA" + str(uuid.uuid4())
    message_type = AFAASMessageType.AGENT_AGENT.value
    agent_sender_id: str
    agent_receiver_id: str
    user_id: str
    message: str
