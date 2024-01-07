from __future__ import annotations

import uuid
from typing import Awaitable, Callable

from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore

from AFAAS.interfaces.adapters import AbstractLanguageModelProvider
from AFAAS.interfaces.agent.assistants.prompt_manager import BasePromptManager
from AFAAS.interfaces.agent.loop import BaseLoopHook
from AFAAS.interfaces.agent.main import BaseAgent
from AFAAS.interfaces.db.db import AbstractMemory
from AFAAS.interfaces.workflow import WorkflowRegistry
from AFAAS.interfaces.workspace import AbstractFileWorkspace
from AFAAS.lib.sdk.logger import AFAASLogger

from .loop import UserContextLoop

LOG = AFAASLogger(name=__name__)


class UserContextAgent(BaseAgent):
    class SystemSettings(BaseAgent.SystemSettings):
        class Config(BaseAgent.SystemSettings.Config):
            pass

    def __init__(
        self,
        settings: UserContextAgent.SystemSettings,
        user_id: uuid.UUID,
        agent_id: uuid.UUID = SystemSettings.generate_uuid(),
        loop: UserContextLoop = UserContextLoop(),
        prompt_manager: BasePromptManager = BasePromptManager(),
        db: AbstractMemory = None,
        default_llm_provider: AbstractLanguageModelProvider = None,
        workspace: AbstractFileWorkspace = None,
        vectorstores: dict[str , VectorStore] = {},
        embeddings: Embeddings = None,
        workflow_registry: WorkflowRegistry = None,
        **kwargs,
    ):
        super().__init__(
            settings=settings,
            db=db,
            workspace=workspace,
            default_llm_provider=default_llm_provider,
            prompt_manager=prompt_manager,
            user_id=user_id,
            agent_id=agent_id,
            vectorstores=vectorstores,
            embedding_model=embeddings,
            workflow_registry=workflow_registry,
            **kwargs,
        )

        self._loop: UserContextLoop = UserContextLoop()
        self._loop.set_agent(agent=self)

    def loophooks(self) -> UserContextLoop.LoophooksDict:
        if not self._loop._loophooks:
            self._loop._loophooks = {}
        return self._loop._loophooks

    def loop(self) -> UserContextLoop:
        return self._loop

    def add_hook(self, hook: BaseLoopHook, uuid: uuid.UUID):
        super().add_hook(hook, uuid)

    ################################################################################
    ################################ LOOP MANAGEMENT################################
    ################################################################################

    async def start(
        self,
        user_input_handler: Callable[[str], Awaitable[str]],
        user_message_handler: Callable[[str], Awaitable[str]],
    ):
        return_var = await super().start(
            user_input_handler=user_input_handler,
            user_message_handler=user_message_handler,
        )
        return return_var

    async def stop(
        self,
        user_input_handler: Callable[[str], Awaitable[str]],
        user_message_handler: Callable[[str], Awaitable[str]],
    ):
        return_var = await super().stop(
            agent=self,
            user_input_handler=user_input_handler,
            user_message_handler=user_message_handler,
        )
        return return_var

    ################################################################################
    ################################FACTORY SPECIFIC################################
    ################################################################################

    def __repr__(self):
        return "UserContextAgent()"
