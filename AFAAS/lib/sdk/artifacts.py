from __future__ import annotations
import uuid
from typing import Optional

from pydantic import Field

from AFAAS.configs.schema import AFAASModel
from AFAAS.interfaces.agent.main import BaseAgent

class Artifact(AFAASModel):
    artifact_id: str = Field(default_factory=lambda: Artifact.generate_uuid())

    agent_id: str = Field(
        ...,
        description="ID of the agent.",
        examples=["b225e278-8b4c-4f99-a696-8facf19f0e56"],
    )
    user_id: str = Field(
        ...,
        description="ID of the user.",
        examples=["b225e278-8b4c-4f99-a696-8facf19f0e56"],
    )
    source: str = Field(
        ...,
        description="Source of the artifact.",
        examples=["www.mywebsite.com"],
    )

    # NOTE: WILL NOT BE SUPPORTED
    agent_created: bool = Field(
        default=True,
        description="Whether the artifact has been created by the agent.",
        examples=[False],
    )
    relative_path: str = Field(
        ...,
        description="Relative path of the artifact in the agents workspace.",
        examples=["/my_folder/my_other_folder/"],
    )
    file_name: str = Field(
        ...,
        description="Filename of the artifact.",
        examples=["main.py"],
    )
    mime_type: str = Field(
        ...,
        description="MIME type of the artifact.",
        examples=["text/plain"],
    )
    license: Optional[str] = Field(
        default=None,
        description="Licence; `None` the document is created by the agent or user",
        examples=["MIT"],
    )
    checksum: str = Field(default=None, description="Checksum of the artifact")

    @staticmethod
    def generate_uuid():
        return str("ATF" + str(uuid.uuid4()))


    async def create_in_db(self, agent: BaseAgent):
        table = await agent.db.get_table("artifacts")
        return await table.add(self)
