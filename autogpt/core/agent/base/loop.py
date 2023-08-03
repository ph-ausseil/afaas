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


class BaseLoop(abc.ABC, metaclass=BaseLoopMeta):  # Import only where it's needed
    class LoophooksDict(TypedDict):
        pass

    @abc.abstractmethod
    def __init__(self, agent: Agent):
        self.is_running: bool = False
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

    async def handle_hooks(self, hook_key: str, hooks: LoophooksDict, agent: Agent):
        # user_input_handler: Callable[[str], Awaitable[str]],
        # user_message_handler: Callable[[str], Awaitable[str]],

        # if hooks.get(hook_key):
        #     for hook in hooks[hook_key]:
        #         await self.execute_hook(hook, agent)
        for hook in agent._loophooks[hook_key]:
            await self.execute_hook(hook, agent)
            # user_input_handler: Callable[[str], Awaitable[str]],
            # user_message_handler: Callable[[str], Awaitable[str]],

    async def execute_hook(self, hook=BaseLoopHook, agent="Agent"):
        hook_name, function, arguments, expected_result, callback = hook
        result = function(*arguments)
        if result != expected_result:
            if callback is not None:
                callback(self, agent, *arguments)
            # else:
            #     self._agent.default_callback[hook_name](result = result ,
            #                                             expected_result = expected_result ,
            #                                             arguments = arguments)

    async def start(
        self,
        agent: Agent,
        user_input_handler: Callable[[str], Awaitable[str]],
        user_message_handler: Callable[[str], Awaitable[str]],
    ) -> None:
        self._active = True

    async def stop(
        self,
        agent: Agent,
        user_input_handler: Callable[[str], Awaitable[str]],
        user_message_handler: Callable[[str], Awaitable[str]],
    ) -> None:
        self._active = False

    def __repr__(self):
        return "AgentLoop()"
