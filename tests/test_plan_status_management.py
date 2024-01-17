from __future__ import annotations
from unittest.mock import AsyncMock

import copy
import json
import uuid

from unittest.mock import patch
import pytest
from pydantic import ValidationError

from AFAAS.interfaces.task.meta import TaskStatusList
from AFAAS.lib.task.plan import Plan
from AFAAS.lib.task.task import Task
from .dataset.agent_planner import agent_dataset
from .dataset.plan_familly_dinner import (
    _plan_familly_dinner,
    plan_familly_dinner_with_tasks_saved_in_db,
    plan_step_0,
    plan_step_1,
    plan_step_2a,
    plan_step_2b,
    _plan_step_2b,
    plan_step_2c,
    plan_step_2d,
    plan_step_3,
    plan_step_4,
    plan_step_5,
    plan_step_6,
    plan_step_7,
    _plan_step_7,
    plan_step_8,
    plan_step_9,
    plan_step_10,
    plan_step_11,
    task_awaiting_preparation,
    task_ready_all_predecessors_done,
    task_ready_all_subtasks_done,
    task_ready_no_predecessors_or_subtasks,
    task_with_mixed_predecessors,
    task_with_ongoing_subtasks,
    task_with_unmet_predecessors,
    default_task,
    plan_with_no_task,
)
from .utils.ascii_tree import print_tree , pytest_terminal_summary , test_trees

import pytest

@pytest.mark.asyncio
async def test_register_new_task(plan_step_0: Plan, default_task: Task):
    # Add a new task to the plan
    plan = plan_step_0
    task = default_task
    initial_task_count = len(plan._all_task_ids)
    plan._register_new_task(task)

    # Assert that the task is added
    assert task.task_id in plan._all_task_ids
    assert len(plan._all_task_ids) == initial_task_count + 1

@pytest.mark.asyncio
async def test_plan_state_consistency(plan_with_no_task: Plan):
    plan = plan_with_no_task
    task = Task(task_id="example task", agent=plan.agent, task_goal = "example task goal")

    # Perform various operations on the plan
    #plan._register_new_task(task)
    plan.add_task(task)
    assert task.task_id in plan._all_task_ids
    assert task.task_id not in plan._ready_task_ids
    assert task.task_id not in plan._done_task_ids
    task.state = TaskStatusList.READY
    assert task.task_id in plan._ready_task_ids
    assert task.task_id not in plan._done_task_ids
    await task.close_task()

    # Check for consistency in plan state
    assert task.task_id in plan._all_task_ids
    assert task.task_id not in plan._ready_task_ids
    assert task.task_id in plan._done_task_ids

@pytest.mark.asyncio
async def test_register_multiple_tasks(plan_step_0: Plan, default_task: Task):
    # Prepare multiple tasks
    plan = plan_step_0
    pytest.skip()
    tasks = [copy.deepcopy(default_task) for _ in range(5)]  # Assuming copy is available
    initial_task_count = len(plan._all_task_ids)
    plan._register_new_tasks(tasks)

    # Assert that all tasks are added
    assert len(plan._all_task_ids) == initial_task_count + len(tasks)


@pytest.mark.asyncio
@pytest.mark.xfail(raises=ValidationError)
async def test_register_task_invalid_data(plan_step_0: Plan):
    # Create a task with invalid data
    task = Task(agent=None, task_id=None, task_goal="Invalid Task")
    plan = plan_step_0

    with pytest.raises(ValidationError):
        plan._register_new_task(task)

@pytest.mark.asyncio
async def test_update_task_status(plan_step_0: Plan, task_ready_no_predecessors_or_subtasks: Task):
    plan = plan_step_0
    task = task_ready_no_predecessors_or_subtasks
    plan = task_ready_no_predecessors_or_subtasks.agent.plan

    # Set task state to DONE
    await task.close_task()

    # Assert that task state is updated in the plan
    assert task.task_id in plan._done_task_ids
    assert task.task_id not in plan._ready_task_ids

@pytest.mark.asyncio
async def test_task_lists_behavior(plan_step_0: Plan, default_task: Task):
    plan = plan_step_0
    task = default_task

    # Register new task and mark as ready
    plan.add_task(task)
    task.state = TaskStatusList.READY

    # Assert that task is in the correct list
    assert task.task_id in plan._ready_task_ids

    # Update task status to DONE
    await task.close_task()

    # Assert that task is moved to the done list
    assert task.task_id in plan._done_task_ids
    assert task.task_id not in plan._ready_task_ids

@pytest.mark.asyncio
async def test_unregister_task(plan_step_0: Plan, default_task: Task):

    # Register and then unregister the task
    plan_step_0._register_new_task(default_task)
    plan_step_0.unregister_loaded_task(default_task.task_id)

    # Assert that task is no longer in the plan
    assert plan_step_0._loaded_tasks_dict.get(default_task.task_id) == None

@pytest.mark.asyncio
async def test_update_individual_task_status(plan_step_0: Plan, default_task: Task):
    plan = plan_step_0
    task = default_task

    # Update task status
    task.state = TaskStatusList.IN_PROGRESS_WITH_SUBTASKS
    assert task.state == TaskStatusList.IN_PROGRESS_WITH_SUBTASKS

    # Assert the plan reflects this update
    assert task.task_id not in plan._ready_task_ids

@pytest.mark.asyncio
async def test_invalid_status_update(default_task: Task):
    pytest.skip()
    task = default_task

    with pytest.raises(ValueError):
        task.state = "invalid_status"  # Assuming ValueError is raised for invalid status

@pytest.mark.asyncio
async def test_automatic_status_update_based_on_predecessors(plan_step_2b: Plan, task_with_mixed_predecessors: Task):
    plan = plan_step_2b
    task = task_with_mixed_predecessors

    # Complete all predecessor tasks
    predecessors = await task.task_predecessors.get_all_tasks_from_stack()
    for predecessor_id in predecessors :
        predecessor_task = await plan.get_task(predecessor_id)
        await predecessor_task.close_task()

    # Check if the task state
    assert task.state == TaskStatusList.READY


@pytest.mark.asyncio
async def test_automatic_status_update_based_on_predecessors_v2(plan_step_2b: Plan, task_with_mixed_predecessors: Task):
    plan = plan_step_2b
    task = task_with_mixed_predecessors

    predecessors = await task.task_predecessors.get_all_tasks_from_stack()
    # Complete all predecessor tasks
    for predecessor_id in predecessors:
        predecessor_task = await plan.get_task(predecessor_id)
        await predecessor_task.close_task()

    # Check if the task state
    task.is_ready()
    assert task.state == TaskStatusList.READY


@pytest.mark.asyncio
async def test_auto_update_status_when_predecessors_done(plan_step_2b: Plan, task_with_mixed_predecessors: Task):
    plan = plan_step_2b
    task = task_with_mixed_predecessors

    # Update all predecessor tasks to DONE
    predecessors = await task.task_predecessors.get_all_tasks_from_stack()
    for predecessor_id in predecessors :
        predecessor_task = await plan.get_task(predecessor_id)
        await predecessor_task.close_task()

    # Assert that the task state is updated
    assert task.state == TaskStatusList.READY  # Assuming task becomes READY after all predecessors are DONE

@pytest.mark.asyncio
async def test_no_auto_update_if_predecessor_not_done(plan_step_2b: Plan, task_with_mixed_predecessors: Task):
    plan = plan_step_2b
    task = task_with_mixed_predecessors

    assert task.state == TaskStatusList.BACKLOG 

    # Update one predecessor to DONE, leave others
    first_predecessor = await task.task_predecessors.get_all_tasks_from_stack()
    first_predecessor_task = first_predecessor[0]
    await first_predecessor_task.close_task()

    # Assert that the task state does not change to READY
    assert task.state != TaskStatusList.READY  # Assuming task does not become READY unless all predecessors are DONE

@pytest.mark.asyncio
async def test_status_update_with_subtasks(plan_step_0: Plan, task_with_ongoing_subtasks: Task):
    plan = plan_step_0
    task = task_with_ongoing_subtasks

    # Complete all subtasks
    subtasks = await task._subtasks.get_all_tasks_from_stack()
    for subtask in subtasks:
        await subtask.close_task()

    await subtasks[-1].close_task()
    # Assert that the parent task state is updated accordingly
    assert task.state == TaskStatusList.DONE  # Assuming task becomes DONE after all subtasks are DONE

@pytest.mark.asyncio
async def test_handling_tasks_with_unmet_predecessors(plan_step_0: Plan, task_with_unmet_predecessors: Task):
    plan = plan_step_0
    task = task_with_unmet_predecessors

    # Assert that the task is not READY
    assert task.state != TaskStatusList.READY  # Assuming task is not READY if it has unmet predecessors

@pytest.mark.asyncio
async def test_task_awaiting_preparation(plan_step_0: Plan, task_awaiting_preparation: Task):
    plan = plan_step_0
    task = task_awaiting_preparation

    # Check initial state of the task
    assert task.state != TaskStatusList.READY  # Assuming

@pytest.mark.asyncio
async def test_task_awaiting_preparation(plan_step_0: Plan, task_awaiting_preparation: Task):
    plan = plan_step_0
    task = task_awaiting_preparation

    # Check initial state of the task
    assert task.state != TaskStatusList.READY  # Assuming

@pytest.mark.asyncio
async def test_automatic_status_update_based_on_predecessors(plan_step_2b: Plan, task_with_mixed_predecessors: Task):
    plan = plan_step_2b
    task = task_with_mixed_predecessors

    # Complete all predecessor tasks
    predecessors = await task.task_predecessors.get_all_tasks_from_stack()
    for predecessor_id in predecessors :
        predecessor_task = await plan.get_task(predecessor_id)
        await predecessor_task.close_task()

    # Check if the task state updates automatically
    assert task.state == TaskStatusList.READY

@pytest.mark.asyncio
async def test_task_parent_retrieval(plan_step_0: Plan, default_task: Task):
    plan = plan_step_0
    task = default_task
    parent_task = await task.task_parent()

    # Assuming the parent task is set correctly
    assert parent_task is not None
    assert parent_task.task_id == task._task_parent_id

@pytest.mark.asyncio
async def test_task_predecessors_successors(plan_step_0: Plan, default_task: Task):
    task = default_task
    predecessor = Task(task_id="predecessor", agent=task.agent, task_goal = "predecessor goal")
    successor = Task(task_id="successor", agent=task.agent, task_goal = "successor goal")

    # Add predecessor and successor
    task.add_predecessor(predecessor)
    task.add_successor(successor)
    task.agent.plan._register_new_task(task= predecessor)
    task.agent.plan._register_new_task(task= successor)

    # Verify they are added correctly
    assert predecessor in await task.task_predecessors.get_all_tasks_from_stack()
    assert successor in await  task.task_successors.get_all_tasks_from_stack()

@pytest.mark.asyncio
async def test_task_state_change_propagation(plan_step_0: Plan, task_with_ongoing_subtasks: Task):
    plan = plan_step_0
    task = task_with_ongoing_subtasks
    await task.close_task()

    # Assuming successors' state depends on this task
    successors =  await task.task_successors.get_all_tasks_from_stack()
    for successor_id in successors:
        successor_task = await plan.get_task(successor_id)
        # Check if successor's state is updated as needed (depends on implementation)
        assert successor_task.state == TaskStatusList.READY


@pytest.mark.asyncio
async def test_plan_loading_and_task_retrieval(plan_step_0: Plan):
    plan = plan_step_0
    task_id = "test_task"
    new_task = Task(task_id=task_id, agent=plan.agent , task_goal = "task_goal")

    # Add a new task and simulate plan loading
    plan.add_task(new_task)
    loaded_plan = await Plan._load(plan.plan_id, plan.agent)

    # Retrieve the task from the loaded plan
    retrieved_task = await loaded_plan.get_task(task_id)
    assert retrieved_task.task_id == task_id


@pytest.mark.asyncio
async def test_edge_cases_and_exception_handling(plan_step_0: Plan):
    plan = plan_step_0
    invalid_task_id = "non_existent"

    # Attempt to retrieve a non-existent task
    with pytest.raises(Exception):
        await plan.get_task(invalid_task_id)

    # Other edge cases as relevant to your implementation



