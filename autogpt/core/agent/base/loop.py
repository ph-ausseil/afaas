from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any, Awaitable, Callable, List, Optional

from typing_extensions import NamedTuple, TypedDict

if TYPE_CHECKING:
    from autogpt.core.agent.base.agent import Agent


class BaseLoopMeta(abc.ABCMeta):
    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        instance.__init__(*args, **kwargs)
        return instance


class BaseLoopHook(NamedTuple):
    name: str
    function: Callable
    args: List[Any]
    expected_return: Any
    callback_function: Optional[Callable[..., Any]]


class BaseLoop(abc.ABC, metaclass=BaseLoopMeta):  
    class LoophooksDict(TypedDict):
        pass

    @abc.abstractmethod
    def __init__(self, agent: Agent):
        self._is_running: bool = False
        self._agent = agent
        self._active = False
        self._task_queue = []
        self._completed_tasks = []
        self._current_task = None
        self._next_ability = None

    @abc.abstractmethod
    async def run(
        self,
        agent: Agent,
        hooks: LoophooksDict,
        user_input_handler: Callable[[str], Awaitable[str]],
        user_message_handler: Callable[[str], Awaitable[str]],
    ) -> None:
        ...

    async def handle_hooks(self, 
                           hook_key: str, 
                           hooks: LoophooksDict, 
                           agent: Agent,
                            user_input_handler: Callable[[str], Awaitable[str]],
                            user_message_handler: Callable[[str], Awaitable[str]]):

        if agent._loophooks.get(hook_key):
            for key, hook in agent._loophooks[hook_key]:
                if isinstance(hook, BaseLoopHook):
                    self._agent._logger.debug(f"Executing hook {key}")
                    self._agent._logger.info(f"hook class is {hook.__class__}'")
                    await self.execute_hook(hook = hook, 
                                            agent = agent,
                                            user_input_handler=user_input_handler,
                                            user_message_handler=user_message_handler)
                else :
                    raise TypeError(f"Hook {key} is not a BaseLoopHook but is a {hook.__class__}")


    async def execute_hook(self, 
                           hook : BaseLoopHook, 
                           agent: Agent,
                            user_input_handler: Callable[[str], Awaitable[str]],
                            user_message_handler: Callable[[str], Awaitable[str]]):
        hook_name, function, arguments, expected_result, callback = hook
        result = function(*arguments)
        if result != expected_result:
            if callback is not None:
                callback(self, agent, *arguments)

    async def start(
        self,
        agent: Agent,
        user_input_handler: Callable[[str], Awaitable[str]],
        user_message_handler: Callable[[str], Awaitable[str]],
    ) -> None:
        self._agent._logger.debug("Starting loop")
        self._active = True
        self._user_input_handler = user_input_handler
        self._user_message_handler = user_message_handler

    async def stop(
        self,
        agent: Agent,
        user_input_handler: Callable[[str], Awaitable[str]],
        user_message_handler: Callable[[str], Awaitable[str]],
    ) -> None:
        self._agent._logger.debug("Stoping loop")
        self._active = False
        self._user_input_handler = user_input_handler
        self._user_message_handler = user_message_handler

    def __repr__(self):
        return "BaseLoop()"
