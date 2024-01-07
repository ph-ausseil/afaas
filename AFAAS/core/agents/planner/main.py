from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Awaitable, Callable

from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore

from AFAAS.core.tools.builtins import (
    TOOL_CATEGORIES,  # FIXME: This is a temporary fix but shall not be delt here
)
from AFAAS.core.tools.simple import DefaultToolRegistry
from AFAAS.interfaces.adapters import AbstractLanguageModelProvider
from AFAAS.interfaces.agent.assistants.prompt_manager import BasePromptManager
from AFAAS.interfaces.agent.assistants.tool_executor import ToolExecutor
from AFAAS.interfaces.agent.main import BaseAgent
from AFAAS.interfaces.db.db import AbstractMemory
from AFAAS.interfaces.tools.base import BaseToolsRegistry
from AFAAS.interfaces.workflow import WorkflowRegistry
from AFAAS.lib.sdk.logger import AFAASLogger
from AFAAS.lib.task.plan import Plan

from .loop import PlannerLoop

LOG = AFAASLogger(name=__name__)

if TYPE_CHECKING:
    from AFAAS.interfaces.workspace import AbstractFileWorkspace


class PlannerAgent(BaseAgent):
    # FIXME: Move to BaseAgent
    @property
    def tool_registry(self) -> BaseToolsRegistry:
        if self._tool_registry is None:
            self._tool_registry = DefaultToolRegistry(
                settings=self._settings,
                db=self.db,
                workspace=self.workspace,
                model_providers=self.default_llm_provider,
                modules=TOOL_CATEGORIES,
            )
        return self._tool_registry

    @tool_registry.setter
    def tool_registry(self, value: BaseToolsRegistry):
        self._tool_registry = value

    class SystemSettings(BaseAgent.SystemSettings):
        class Config(BaseAgent.SystemSettings.Config):
            pass

        def json(self, *args, **kwargs):
            self.prepare_values_before_serialization()  # Call the custom treatment before .json()
            kwargs["exclude"] = self.Config.default_exclude
            return super().json(*args, **kwargs)

    def __init__(
        self,
        settings: PlannerAgent.SystemSettings,
        user_id: str,
        agent_id: str = SystemSettings.generate_uuid(),
        prompt_manager: BasePromptManager = BasePromptManager(),
        loop: PlannerLoop = PlannerLoop(),
        tool_handler: ToolExecutor = ToolExecutor(),
        tool_registry=None,
        db: AbstractMemory = None,
        default_llm_provider: AbstractLanguageModelProvider = None,
        workspace: AbstractFileWorkspace = None,
        vectorstores: dict[str , VectorStore] = {},  # Optional parameter for custom vectorstore
        embedding_model: Embeddings = None,  # Optional parameter for custom embedding model
        workflow_registry: WorkflowRegistry = None,
        **kwargs,
    ):
        # FIXME:
        ## Workarround for attribute where dependancy injection remain to implement
        if agent_id is None:
            agent_id: str = self.SystemSettings.generate_uuid()
        if prompt_manager is None:
            prompt_manager: BasePromptManager = BasePromptManager()
        if loop is None:
            loop: PlannerLoop = PlannerLoop()
        if tool_handler is None:
            tool_handler: ToolExecutor = ToolExecutor()

        super().__init__(
            settings=settings,
            db=db,
            workspace=workspace,
            default_llm_provider=default_llm_provider,
            prompt_manager=prompt_manager,
            user_id=user_id,
            agent_id=agent_id,
            vectorstores=vectorstores,
            embedding_model=embedding_model,
            workflow_registry=workflow_registry,
            **kwargs,
        )

        self.agent_goals = (
            settings.agent_goals
        )  # TODO: Remove & make it part of the plan ?
        self.agent_goal_sentence = settings.agent_goal_sentence

        #
        # Step 4 : Set the ToolRegistry
        #
        self._tool_registry = tool_registry
        self.tool_registry.set_agent(agent=self)

        ###
        ### Step 5 : Create the Loop
        ###
        self._loop: PlannerLoop = loop
        self._loop.set_agent(agent=self)

        # Set tool Executor
        self._tool_executor: ToolExecutor = tool_handler
        self._tool_executor.set_agent(agent=self)

    @classmethod
    async def load(
        cls,
        settings: PlannerAgent.SystemSettings,
        user_id: str,
        ###
        agent_id: uuid.UUID = None, 
        prompt_manager: BasePromptManager = None, 
        loop: PlannerLoop = None, 
        tool_handler: ToolExecutor = None, 
        ###
        tool_registry=None,
        db: AbstractMemory = None,
        default_llm_provider: AbstractLanguageModelProvider = None,
        workspace: AbstractFileWorkspace = None,
        vectorstores: dict[str, VectorStore] = {},
        embedding_model: Embeddings = None,
        workflow_registry: WorkflowRegistry = None,
        **kwargs
    ):
        agent = cls(
            settings=settings,
            user_id=user_id,
            agent_id=agent_id,
            prompt_manager=prompt_manager,
            loop=loop,
            tool_handler=tool_handler,
            tool_registry=tool_registry,
            db=db,
            default_llm_provider=default_llm_provider,
            workspace=workspace,
            vectorstores=vectorstores,
            embedding_model=embedding_model,
            workflow_registry=workflow_registry,
            **kwargs
        )

        # Creating or getting the plan
        if hasattr(agent, "plan_id") and agent.plan_id is not None:
            agent.plan = await Plan.get_plan_from_db(
                plan_id=agent.plan_id, agent=agent
            )
            agent._loop.set_current_task(task=await agent.plan.get_next_task())
        else:
            agent.plan = await Plan.db_create(agent=agent)
            agent.plan_id = agent.plan.plan_id
            agent._loop.set_current_task(task=await agent.plan.get_ready_tasks()[0])
            await agent.db_create()

        from AFAAS.lib.message_agent_user import MessageAgentUser, emiter
        from AFAAS.lib.message_common import AFAASMessageStack
        # Message agent user initialization
        agent.message_agent_user = AFAASMessageStack(db=agent.db)
        # FIXME:v.0.0.1 : The first message seem not to be saved in the DB #91 https://github.com/ph-ausseil/afaas/issues/91
        await agent.message_agent_user.add(
            message=MessageAgentUser(
                emitter=emiter.AGENT.value,
                user_id=agent.user_id,
                agent_id=agent.agent_id,
                message="What would you like to do ?",
            )
        )
        await agent.message_agent_user.add(
            message=MessageAgentUser(
                emitter=emiter.USER.value,
                user_id=agent.user_id,
                agent_id=agent.agent_id,
                message=agent.agent_goal_sentence,
            )
        )

        return agent

    """ #NOTE: This is a remnant of a plugin system on stand-by that have not been implemented yet.
        ###
        ### Step 6 : add hooks/pluggins to the loop
        ###
        # TODO: Get hook added from configuration files
        # Exemple :
        # self.add_hook( hook: BaseLoopHook, uuid: uuid.UUID)
        self.add_hook(
            hook=BaseLoopHook(
                name="begin_run",
                function=self.test_hook,
                kwargs=["foo_bar"],
                expected_return=True,
                callback_function=None,
            ),
            uuid=uuid.uuid4(),
        )

    @staticmethod
    def test_hook(**kwargs):
        LOG.notice("Entering test_hook Function")
        LOG.notice(
            "Hooks are an experimental plug-in system that may fade away as we are transiting from a Loop logic to a Pipeline logic."
        )
        test = "foo_bar"
        for key, value in kwargs.items():
            LOG.debug(f"{key}: {value}")

    def loophooks(self) -> PlannerLoop.LoophooksDict:
        if not self._loop._loophooks:
            self._loop._loophooks = {}
        return self._loop._loophooks
    """

    ################################################################################
    ################################ LOOP MANAGEMENT################################
    ################################################################################

    def loop(self) -> PlannerLoop:
        return self._loop

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

