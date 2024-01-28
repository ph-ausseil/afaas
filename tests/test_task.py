from __future__ import annotations

import copy
import json
import uuid
from unittest.mock import AsyncMock, patch

import pytest

from AFAAS.interfaces.task.meta import TaskStatusList
from AFAAS.lib.task.plan import Plan
from AFAAS.lib.task.task import Task

from .dataset.agent_planner import agent_dataset
from .dataset.plan_familly_dinner import (
    _plan_familly_dinner,
    _plan_step_3,
    _plan_step_10,
    _plan_step_11,
    _plan_step_12,
    _plan_step_13,
    _plan_step_14,
    _plan_step_15,
    _plan_step_16,
    _plan_step_17,
    _plan_step_18,
    _plan_step_19,
    _plan_step_20,
    _plan_step_21,
    _plan_step_22,
    _plan_step_23,
    _plan_step_24,
    default_task,
    plan_familly_dinner_with_tasks_saved_in_db,
    plan_step_0,
    plan_step_1,
    plan_step_2,
    plan_step_3,
    plan_step_4,
    plan_step_5,
    plan_step_6,
    plan_step_7,
    plan_step_8,
    plan_step_9,
    plan_step_10,
    plan_step_11,
    plan_step_12,
    plan_step_13,
    plan_step_14,
    task_awaiting_preparation,
    task_ready_no_predecessors_or_subtasks,
    task_with_mixed_predecessors,
    task_with_ongoing_subtasks,
    task_with_unmet_predecessors,
)



def test_task_attribute_setting_and_getting(default_task):
    """Test setting and getting of task attributes."""
    default_task.task_id = "new_id"
    assert default_task.task_id == "new_id"
    # Add similar tests for other attributes


@pytest.mark.asyncio
async def test_prevention_of_recursive_loops(default_task):
    pytest.skip("NOT IMPLEMENTED IN THE LIBRARY BY SHOULD BE !") #FIXME
    with pytest.raises(Exception):  # Replace with specific exception if applicable
        default_task.add_predecessor(default_task)
    with pytest.raises(Exception):  # Replace with specific exception if applicable
        default_task.add_successor(default_task)

def test_set_state_validator(default_task):
    pytest.skip("NOT IMPLEMENTED IN THE LIBRARY BY SHOULD BE !") #FIXME
    valid_state = TaskStatusList.READY  # Replace with an actual valid state
    default_task.state = valid_state
    assert default_task.state == valid_state

    # Test setting an invalid state
    invalid_state = "invalid_state"  # Replace with an actual invalid state
    with pytest.raises(ValueError):  # Assuming ValueError is raised for invalid state
        default_task.state = invalid_state

@pytest.mark.asyncio
async def test_close_task_sets_state_to_done(default_task):
    await default_task.close_task()
    assert default_task.state == TaskStatusList.DONE  # Adjust as needed

@pytest.mark.asyncio
async def test_close_task_with_all_sibling_tasks_done(default_task, task_with_unmet_predecessors):
    # Setup the scenario where all sibling tasks are done
    default_task.add_successor(task_with_unmet_predecessors)
    task_with_unmet_predecessors.state = TaskStatusList.DONE
    await default_task.close_task()
    assert default_task.state == TaskStatusList.DONE  # Adjust as needed

@pytest.mark.asyncio
async def test_get_task_path(default_task: Task):
    path = await default_task.get_task_path(include_self=True)
    # Assuming the task path should include the task itself when include_self is True
    assert default_task in path
    path = await default_task.get_task_path()
    # Assuming the task path should include the task itself when include_self is True
    assert default_task not in path

@pytest.mark.asyncio
async def test_get_formatted_task_path(default_task: Task):
    formatted_path = await default_task.get_formated_task_path()
    assert isinstance(formatted_path, str)  # Further assertions based on expected format

@pytest.mark.asyncio
async def test_get_siblings_and_siblings_ids(default_task : Task, task_with_unmet_predecessors: Task):
    parent = await default_task.task_parent()
    parent.add_task(task=task_with_unmet_predecessors)
    siblings = await default_task.get_siblings()
    siblings_ids = await default_task.get_siblings_ids()
    assert task_with_unmet_predecessors in siblings
    assert task_with_unmet_predecessors.task_id in siblings_ids


@pytest.mark.asyncio
async def test_get_task_from_db(default_task: Task):
    # Assuming mocked_db is a fixture to mock the database interaction
    mocked_db = default_task.agent.db
    fetched_task = await Task.get_task_from_db(default_task.task_id, default_task.agent)
    assert fetched_task.task_id == default_task.task_id

@pytest.mark.asyncio
async def test_task_hashing(default_task: Task):
    # Test that two tasks with the same ID have the same hash
    task_clone = await default_task.clone()
    assert hash(default_task) != hash(task_clone)

    # Test that different tasks have different hashes
    task_clone.task_id = default_task.task_id
    assert hash(default_task) == hash(task_clone)


# @pytest.mark.asyncio
# async def test_adding_predecessors_and_successors(default_task : Task, task_with_unmet_predecessors : Task):
#     # Test adding a predecessor
#     default_task.add_predecessor(task_with_unmet_predecessors)
#     assert task_with_unmet_predecessors in await default_task.task_predecessors.get_active_tasks_from_stack()

#     # Test adding a successor
#     default_task.add_successor(task_with_unmet_predecessors)
#     assert default_task in await task_with_unmet_predecessors.task_successors.get_active_tasks_from_stack()

# @pytest.mark.asyncio
# async def test_task_parent_success(plan_step_17 : Plan):
#     """Test the task_parent method for successfully returning a parent task."""
#     task = await plan_step_17.get_task(task_id="300.3.3")
#     parent_task = task.task_parent()
#     assert parent_task is not None
#     # Additional assertions as needed

# @pytest.mark.asyncio
# async def test_task_parent_not_found(plan_step_21 : Plan):
#     """Test the task_parent method's behavior when no parent task is found."""

#     task = await plan_step_21.get_task(task_id="201")
#     plan = await task.task_parent()
#     with pytest.raises(Exception):
#         await plan.task_parent()


# @pytest.mark.asyncio
# async def test_db_create_and_save(default_task):
#     mocked_db = AsyncMock(default_task.agent.db)
#     await Task.db_create(default_task, default_task.agent)
#     mocked_db.get_table.assert_called()  # Further assertions as needed

#     await default_task.db_save()
#     mocked_db.get_table.assert_called()  # Further assertions as needed
