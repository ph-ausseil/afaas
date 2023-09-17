from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any, Awaitable, Callable, List, Optional, Dict

from typing_extensions import NamedTuple, TypedDict

if TYPE_CHECKING:
    from autogpt.core.agent.base.agent import Agent


class BaseLoopMeta(abc.ABCMeta):
    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        instance.__init__(*args, **kwargs)
        return instance

class BaseLoopHookKwargs(TypedDict):
    agent: Agent
    loop: BaseLoop
    user_input_handler: Callable[[str], Awaitable[str]]
    user_message_handler: Callable[[str], Awaitable[str]]
    kwargs: Dict[str, Any] 

class BaseLoopHook(TypedDict):
    name: str
    function: Callable
    kwargs: BaseLoopHookKwargs 
    expected_return: Any
    callback_function: Optional[Callable[..., BaseLoopHookKwargs]]


class BaseLoop(abc.ABC, metaclass=BaseLoopMeta):  
    class LoophooksDict(TypedDict):
        begin_run: Dict[BaseLoopHook]
        end_run: Dict[BaseLoopHook]

    _loophooks: LoophooksDict
    
    @abc.abstractmethod
    def __init__(self, agent: Agent):

        # Step 1 : Setting loop variables
        self._is_running: bool = False
        self._agent = agent
        self._loophooks = self.LoophooksDict()
        for key in self.LoophooksDict.__annotations__.keys():
            self._loophooks[key] = {}

        # Step 2 : Setting task variables
        self._task_queue = []
        self._completed_tasks = []
        self._current_task = None
        self._next_ability = None
        
        # Setting default handlers
        self._user_input_handler: Optional[Callable[[str], Awaitable[str]]] = None
        self._user_message_handler: Optional[Callable[[str], Awaitable[str]]] = None

    @abc.abstractmethod
    async def run(
        self,
        agent: Agent,
        hooks: LoophooksDict,
        user_input_handler: Optional[Callable[[str], Awaitable[str]]] = None, 
        user_message_handler: Optional[Callable[[str], Awaitable[str]]] = None,
    ) -> None:
        ...

    async def handle_hooks(self, hook_key: str, hooks: LoophooksDict, agent: Agent, 
                           user_input_handler: Optional[Callable[[str], Awaitable[str]]] = None, 
                           user_message_handler: Optional[Callable[[str], Awaitable[str]]] = None):
        if isinstance(user_input_handler, Callable) and user_input_handler is not None:
            self._user_input_handler = user_input_handler
        elif self._user_input_handler is None:
            raise TypeError("`user_input_handler` must be a callable or set previously.")
            
        if isinstance(user_message_handler, Callable) and user_message_handler is not None:
            self._user_message_handler = user_message_handler
        elif self._user_message_handler is None:
            raise TypeError("`user_message_handler` must be a callable or set previously.")

        if self._loophooks.get(hook_key):
            for key, hook in self._loophooks[hook_key].items():
                # if isinstance(hook, BaseLoopHook):
                self._agent._logger.debug(f"Executing hook {key}")
                self._agent._logger.info(f"hook class is {hook.__class__}'")
                await self.execute_hook(hook=hook, agent=agent)
                # else :
                #     raise TypeError(f"Hook {key} is not a BaseLoopHook but is a {hook.__class__}")


    async def execute_hook(self, hook: BaseLoopHook, agent: Agent):

        user_input_handler = self._user_input_handler
        user_message_handler = self._user_message_handler
        kwargs: BaseLoopHookKwargs = {
            'agent': agent,
            'loop': self,
            'user_input_handler': user_input_handler,
            'user_message_handler': user_message_handler,
            'kwargs': hook['kwargs']
        }
        # result = hook['function'](agent = agent, 
        #                   loop = self,
        #                   user_input_handler = user_input_handler,
        #                   user_message_handler = user_message_handler,
        #                     *hook['args'])


        result = hook['function'](**kwargs)

        if result != hook['expected_return']:
            if hook['callback_function'] is not None:
                kwargs['result'] = result
                hook['callback_function'](**kwargs)

    async def start(
        self,
        agent: Agent = None,
        user_input_handler: Optional[Callable[[str], Awaitable[str]]] = None, 
        user_message_handler: Optional[Callable[[str], Awaitable[str]]] = None
    ) -> None:
        if isinstance(user_input_handler, Callable) and user_input_handler is not None:
            self._user_input_handler = user_input_handler
        elif self._user_input_handler is None:
            raise TypeError("`user_input_handler` must be a callable or set previously.")
            
        if isinstance(user_message_handler, Callable) and user_message_handler is not None:
            self._user_message_handler = user_message_handler
        elif self._user_message_handler is None:
            raise TypeError("`user_message_handler` must be a callable or set previously.")
            
        self._agent._logger.debug("Starting loop")
        self._active = True

    async def stop(
        self,
        agent: Agent = None,
        user_input_handler: Optional[Callable[[str], Awaitable[str]]] = None, 
        user_message_handler: Optional[Callable[[str], Awaitable[str]]] = None
    ) -> None:
        if isinstance(user_input_handler, Callable) and user_input_handler is not None:
            self._user_input_handler = user_input_handler
        elif self._user_input_handler is None:
            raise TypeError("`user_input_handler` must be a callable or set previously.")
            
        if isinstance(user_message_handler, Callable) and user_message_handler is not None:
            self._user_message_handler = user_message_handler
        elif self._user_message_handler is None:
            raise TypeError("`user_message_handler` must be a callable or set previously.")
         
        self._agent._logger.debug("Stoping loop")
        self._active = False

    def __repr__(self):
        return "BaseLoop()"
