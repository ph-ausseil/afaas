from __future__ import annotations

import uuid
from abc import abstractmethod
from typing import Optional

from pydantic import Field

from AFAAS.interfaces.agent import BaseAgent
from AFAAS.interfaces.task.base import AbstractBaseTask
from AFAAS.interfaces.task.meta import TaskStatusList
from AFAAS.interfaces.task.stack import TaskStack


class AbstractTask(AbstractBaseTask):
    @abstractmethod
    def __init__(self, **data):
        super().__init__(**data)

    # Properties
    @property
    @abstractmethod
    def task_id(self) -> str:
        ...

    # @property
    # @abstractmethod
    # def plan_id(self) -> str:
    #     ...

    @property
    @abstractmethod
    def task_parent(self) -> AbstractBaseTask:
        ...

    @task_parent.setter
    @abstractmethod
    def task_parent(self, task: AbstractBaseTask):
        ...

    @property
    @abstractmethod
    def task_predecessors(self) -> TaskStack:
        ...

    @property
    @abstractmethod
    def task_successors(self) -> TaskStack:
        ...

    state: Optional[TaskStatusList] = Field(default=TaskStatusList.BACKLOG)

    task_text_output: Optional[str]

    task_text_output_as_uml: Optional[str]

    # Methods
    @staticmethod
    def generate_uuid():
        return "T" + str(uuid.uuid4())

    @abstractmethod
    def is_ready(self) -> bool:
        ...

    @abstractmethod
    def add_predecessor(self, task: "AbstractTask"):
        ...

    @abstractmethod
    def add_successor(self, task: "AbstractTask"):
        ...

    @classmethod
    @abstractmethod
    def get_task_from_db(cls, task_id: str, agent: BaseAgent) -> "AbstractTask":
        ...

    @classmethod
    @abstractmethod
    def create_in_db(cls, task: "AbstractTask", agent: BaseAgent):
        ...

    @abstractmethod
    def save_in_db(self):
        ...

    @abstractmethod
    def get_task_path(
        self, task_to_root: bool = False, include_self: bool = False
    ) -> list["AbstractTask"]:
        ...

    @abstractmethod
    def get_formated_task_path(self) -> str:
        ...

    @abstractmethod
    def get_sibblings(self) -> list["AbstractTask"]:
        ...

    @abstractmethod
    def __hash__(self):
        ...

    @abstractmethod
    def __eq__(self, other):
        ...

    def str_with__status__(self):
        return f"{self.task_goal} (id : {self.task_id} / status : {self.state})"

    @abstractmethod
    async def prepare_rag(
        self,
        predecessors: bool = True,
        successors: bool = False,
        history: int = 10,
        sibblings: bool = True,
        path: bool = True,
        similar_tasks: int = 0,
        avoid_redondancy: bool = False,
    ):
        ...
