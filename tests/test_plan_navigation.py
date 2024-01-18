from __future__ import annotations
from unittest.mock import AsyncMock

import copy
import json
import uuid

from unittest.mock import patch
import pytest

from AFAAS.interfaces.task.meta import TaskStatusList
from AFAAS.lib.task.plan import Plan
from AFAAS.lib.task.task import Task
from .dataset.agent_planner import agent_dataset
from .utils.ascii_tree import make_tree
from .dataset.plan_familly_dinner import (
    _plan_familly_dinner,
    plan_familly_dinner_with_tasks_saved_in_db,
    plan_step_0,
    plan_step_1,
    plan_step_2,
    plan_step_3,
    _plan_step_3,
    plan_step_4,
    plan_step_5,
    plan_step_6,
    plan_step_7,
    plan_step_8,
    plan_step_9,
    plan_step_10,
    _plan_step_10,
    plan_step_11,
    plan_step_12,
    plan_step_13,
    plan_step_14,
    task_awaiting_preparation,
    task_ready_no_predecessors_or_subtasks,
    task_with_mixed_predecessors,
    task_with_ongoing_subtasks,
    task_with_unmet_predecessors,
    default_task
)
from .utils.ascii_tree import print_tree , pytest_terminal_summary , test_trees

import pytest

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "plan_step, current_task_id, expected_next_task_id",
    [
        # Current Task Provided
        (plan_familly_dinner_with_tasks_saved_in_db, '101', '102'),
       # (_plan_step_3, '300.1.2', '107'),
        (_plan_step_10, '108', '201'),
        (plan_familly_dinner_with_tasks_saved_in_db, None, '101'),
    ]
    )
async def test_get_next_task(plan_step, current_task_id, expected_next_task_id, request):
    plan : Plan = await plan_step()
    if current_task_id is not None:
        current_task = await plan.get_task(task_id=current_task_id)
    else:
        current_task = None

    next_task = await plan.get_next_task(task=current_task)
    try : 
        assert next_task.task_id == expected_next_task_id
    except AssertionError:
        raise AssertionError( f"next_task.task_id = {next_task.task_id} \n " 
                             f"expected_next_task_id = {expected_next_task_id} \n " 
                             f"{await make_tree(plan)}"
                             )

