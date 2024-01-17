from __future__ import annotations

import copy
import json
import uuid

import pytest

from AFAAS.interfaces.task.meta import TaskStatusList
from AFAAS.lib.task.plan import Plan
from AFAAS.lib.task.task import Task
from tests.dataset.agent_planner import agent_dataset


async def _plan_familly_dinner():
    agent = await agent_dataset()
    plan_dict = {
        "created_at": "2023-12-31T15:38:45.666346",
        "modified_at": "2023-12-31T15:38:45.666355",
        "task_context": None,
        "task_history": None,
        "acceptance_criteria": [],
        "tasks": [],
        "agent_id": agent.agent_id,
        "_task_predecessors": [],
        "_task_successors": [],
        "_subtasks": [],
        "_modified_tasks_ids": [],
        "_new_tasks_ids": [],
    }

    plan_prepare_dinner = Plan(
        plan_id="pytest_P" + str(uuid.uuid4()),
        task_goal="100. Prepare Dinner for Family",
        long_description="Coordinate and execute all necessary activities to prepare a dinner for the family, including grocery shopping, kitchen preparation, cooking, and setting the mood.",
        agent=agent,
        **plan_dict,
    )
    agent.plan = plan_prepare_dinner
    plan_prepare_dinner._subtasks._task_ids = []
    plan_prepare_dinner._all_task_ids = []
    plan_prepare_dinner._ready_task_ids = []
    return plan_prepare_dinner

async def plan_familly_dinner_with_tasks_saved_in_db():

    plan_prepare_dinner = await _plan_familly_dinner()
    agent = plan_prepare_dinner.agent
    task_101_buy_groceries = Task(
        agent=agent, 
        task_id="101", 
        task_goal="101. Buy Groceries",
        long_description="Procure all necessary ingredients and items from a grocery store required for preparing the dinner."
    )
    task_102_clean_kitchen = Task(
        agent=agent, 
        task_id="102", 
        task_goal="102. Clean Kitchen",
        long_description="Thoroughly clean and organize the kitchen area to create a hygienic and efficient cooking environment."
    )
    task_103_choose_music = Task(
        agent=agent, 
        task_id="103", 
        task_goal="103. Choose Dinner Music",
        long_description="Select and arrange a playlist of music that will create a pleasant and relaxing atmosphere during the dinner."
    )
    task_104_decorate_dining_room = Task(
        agent=agent, 
        task_id="104", 
        task_goal="104. Decorate Dining Room",
        long_description="Enhance the dining room's ambiance by arranging decorations, setting appropriate lighting, and ensuring a visually pleasing and comfortable dining environment."
    )

    task_105_set_mood = Task(
        agent=agent, 
        task_id="105", 
        task_goal="105. Set the Mood for Dinner",
        long_description="Create a welcoming and enjoyable dinner atmosphere by adjusting the lighting, music, and room temperature, and ensuring all elements contribute to a pleasant dining experience."
    )
    task_101_buy_groceries.state = TaskStatusList.READY
    task_102_clean_kitchen.state = TaskStatusList.READY
    task_103_choose_music.state = TaskStatusList.READY
    task_104_decorate_dining_room.state = TaskStatusList.READY
    task_105_set_mood.add_predecessor(task_103_choose_music)
    task_105_set_mood.add_predecessor(task_104_decorate_dining_room)


    task_106_set_table = Task(
        agent=agent, 
        task_id="106", 
        task_goal="106. Set the Table",
        long_description="Arrange the dining table with necessary cutlery, plates, glasses, and napkins, ensuring it's elegantly set and ready for the meal."
    )
    task_106_set_table.add_predecessor(task_105_set_mood)

    task_107_make_salad = Task(
        agent=agent, 
        task_id="107", 
        task_goal="107. Make Salad",
        long_description="Prepare a fresh salad by selecting and combining a variety of ingredients, dressing it appropriately, and presenting it in an appealing manner."
    )
    task_107_make_salad.add_predecessor(task_106_set_table)

    task_108_serve_salad = Task(
    agent=agent, 
    task_id="108", 
    task_goal="108. Serve Salad",
    long_description="Present the prepared salad to the diners, ensuring it's served at the right temperature and in an appealing way, as a starter for the dinner."
    )
    task_108_serve_salad.add_predecessor(task_107_make_salad)

    task_200_prepare_main_course = Task(
    agent=agent, 
    task_id="200", 
    task_goal="200. Prepare Main Course",
    long_description="Cook the main course of the dinner, focusing on flavor, presentation, and ensuring it meets the dietary preferences and needs of the family."
    )
    task_200_prepare_main_course.add_predecessor(task_106_set_table)

    task_201_serve_dinner = Task(
    agent=agent, 
    task_id="201", 
    task_goal="201. Serve Main Course",
    long_description="Gracefully serve the prepared main course to the diners, ensuring each person receives their portion with appropriate accompaniments."
    )
    task_201_serve_dinner.add_predecessor(task_200_prepare_main_course)
    task_201_serve_dinner.add_predecessor(task_108_serve_salad)

    task_300_make_banana_bread = Task(
        agent=agent, 
        task_id="300", 
        task_goal="300. Make Banana Bread",
        long_description="Bake a banana bread by following a specific recipe, focusing on achieving the right texture and flavor, and ensuring it's enjoyable for all diners."
    )


    task_300_1_gather_ingredients = Task(
        agent=agent, 
        task_id="300.1", 
        task_goal="300.1. Gather Ingredients",
        long_description="Collect all necessary ingredients for baking banana bread, ensuring they are fresh and of good quality."
    )
    task_300_1_gather_ingredients.add_predecessor(task_101_buy_groceries)
    task_300_1_gather_ingredients.add_predecessor(task_102_clean_kitchen)

    task_300_2_prepare_baking_pan = Task(
        agent=agent, 
        task_id="300.2", 
        task_goal="300.2. Prepare Baking Pan",
        long_description="Ready the baking pan for the banana bread by properly greasing it or lining it with parchment paper, ensuring the bread will not stick and will bake evenly."
    )


    task_300_3_mix_ingredients = Task(
        agent=agent, 
        task_id="300.3", 
        task_goal="300.3. Mix Ingredients",
        long_description="Combine the banana bread ingredients in the correct sequence and method, ensuring a consistent and well-mixed batter."
    )
    task_300_3_mix_ingredients.add_predecessor(task_300_1_gather_ingredients)

    task_300_4_bake_bread = Task(
    agent=agent, 
    task_id="300.4", 
    task_goal="300.4. Bake the Bread",
    long_description="Bake the banana bread in a preheated oven, monitoring it to achieve the perfect bake, both in terms of texture and color."
)
    task_300_4_bake_bread.add_predecessor(task_201_serve_dinner)
    task_300_4_bake_bread.add_predecessor(task_300_3_mix_ingredients)

    task_300_5_cool_bread = Task(
    agent=agent, 
    task_id="300.5", 
    task_goal="300.5. Cool the Bread",
    long_description="Allow the baked banana bread to cool down to an appropriate temperature before serving, ensuring it retains its texture and flavor."
)
    task_300_5_cool_bread.add_predecessor(task_300_4_bake_bread)

    task_300_6_serve_bread = Task(
    agent=agent, 
    task_id="300.6", 
    task_goal="300.6. Serve Banana Bread",
    long_description="Serve the cooled banana bread, slicing it neatly and presenting it in an appetizing manner, potentially with accompaniments like butter or cream."
)
    task_300_6_serve_bread.add_predecessor(task_300_5_cool_bread)
    task_300_6_serve_bread.add_predecessor(task_201_serve_dinner)

    # Subtasks for 'Mix Ingredients'
    task_300_3_1_measure_flour = Task(
        agent=agent, task_id="300.3.1", task_goal="300.3.1. Measure Flour"
    )
    task_300_3_1_measure_flour.add_predecessor(task_300_1_gather_ingredients)

    task_300_3_2_mash_bananas = Task(
        agent=agent, task_id="300.3.2", task_goal="300.3.2. Mash Bananas"
    )
    task_300_3_2_mash_bananas.add_predecessor(task_300_1_gather_ingredients)

    task_300_3_3_combine_wet_ingredients = Task(
        agent=agent, task_id="300.3.3", task_goal="300.3.3. Combine Wet Ingredients"
    )
    task_300_3_3_combine_wet_ingredients.add_predecessor(task_300_3_1_measure_flour)
    task_300_3_3_combine_wet_ingredients.add_predecessor(task_300_3_2_mash_bananas)

    task_300_2_1_grease_pan = Task(
        agent=agent, task_id="300.2.1", task_goal="300.2.1. Grease Baking Pan"
    )
    task_300_2_1_grease_pan.add_predecessor(task_300_1_gather_ingredients)

    task_300_2_2_line_pan = Task(
        agent=agent,
        task_id="300.2.2",
        task_goal="300.2.2. Line Baking Pan with Parchment Paper",
    )
    task_300_2_2_line_pan.add_predecessor(task_300_2_1_grease_pan)

    task_300_1_1_find_ingredients_list = Task(
        agent=agent, task_id="300.1.1", task_goal="300.1.1. Find Ingredients List"
    )
    task_300_1_1_find_ingredients_list.add_predecessor(task_101_buy_groceries)

    task_300_1_2_check_pantry = Task(
        agent=agent,
        task_id="300.1.2",
        task_goal="300.1.2. Check Pantry for Ingredients",
    )
    task_300_1_2_check_pantry.add_predecessor(task_300_1_1_find_ingredients_list)

    plan_prepare_dinner.add_task(task_101_buy_groceries)

    plan_prepare_dinner.add_task(task_102_clean_kitchen)
    plan_prepare_dinner.add_task(task_103_choose_music)
    plan_prepare_dinner.add_task(task_104_decorate_dining_room)
    plan_prepare_dinner.add_task(task_105_set_mood)
    plan_prepare_dinner.add_task(task_106_set_table)
    plan_prepare_dinner.add_task(task_107_make_salad)
    plan_prepare_dinner.add_task(task_108_serve_salad)
    plan_prepare_dinner.add_task(task_200_prepare_main_course)
    plan_prepare_dinner.add_task(task_201_serve_dinner)
    plan_prepare_dinner.add_task(task_300_make_banana_bread)
    task_200_prepare_main_course.add_task(task_300_1_gather_ingredients)
    task_300_1_gather_ingredients.add_task(task_300_1_1_find_ingredients_list)
    task_300_1_gather_ingredients.add_task(task_300_1_2_check_pantry)
    task_200_prepare_main_course.add_task(task_300_2_prepare_baking_pan)
    task_300_2_prepare_baking_pan.add_task(task_300_2_1_grease_pan)
    task_300_2_prepare_baking_pan.add_task(task_300_2_2_line_pan)
    task_200_prepare_main_course.add_task(task_300_3_mix_ingredients)
    task_300_3_mix_ingredients.add_task(task_300_3_1_measure_flour)
    task_300_3_mix_ingredients.add_task(task_300_3_2_mash_bananas)
    task_300_3_mix_ingredients.add_task(task_300_3_3_combine_wet_ingredients)
    task_200_prepare_main_course.add_task(task_300_4_bake_bread)
    task_200_prepare_main_course.add_task(task_300_5_cool_bread)
    task_200_prepare_main_course.add_task(task_300_6_serve_bread)

    await plan_prepare_dinner.db_create()
    await plan_prepare_dinner.db_save()    
    return plan_prepare_dinner

async def move_to_next(plan : Plan) :
    task_id: str
    plan._all_task_ids.reverse()

    for task_id in plan._all_task_ids:
        task = await plan.get_task(task_id=task_id)
        if task.state == TaskStatusList.READY and task.is_ready():
            task.close_task()
            task.task_text_output = f"Completed '{task.task_goal}' successfully."
        elif task.is_ready():
            task.state = TaskStatusList.READY

    plan._all_task_ids.reverse()

    for task_id in plan._all_task_ids:
        task = await plan.get_task(task_id=task_id)
        print(f"Task {task.task_goal} is {task.state}")
    return plan


@pytest.fixture
async def plan_with_no_task() :
    return await _plan_familly_dinner()


@pytest.fixture
async def plan_step_0():
    # Initial setup with multiple subtasks
    return await plan_familly_dinner_with_tasks_saved_in_db()


@pytest.fixture
async def plan_step_1() -> Plan:
    return await _plan_step_1()

async def _plan_step_1() -> Plan:
    t = await plan_familly_dinner_with_tasks_saved_in_db()
    return await move_to_next(t)

@pytest.fixture
async def plan_step_2a() -> Plan:
    return await _plan_step_2a()

async def _plan_step_2a() -> Plan:
    t = await _plan_step_1()
    return await move_to_next(t)


@pytest.fixture
async def plan_step_2b() -> Plan:
    return await _plan_step_2b()

async def _plan_step_2b() -> Plan:
    t = await _plan_step_2a()
    return await move_to_next(t)


@pytest.fixture
async def plan_step_2c() -> Plan:
    return await _plan_step_2c()

async def _plan_step_2c() -> Plan:
    t = await _plan_step_2b()
    return await move_to_next(t)


@pytest.fixture
async def plan_step_2d() -> Plan:
    return await _plan_step_2d()

async def _plan_step_2d() -> Plan:
    t = await _plan_step_2c()
    return await move_to_next(t)


@pytest.fixture
async def plan_step_3() -> Plan:
    return await _plan_step_3()

async def _plan_step_3() -> Plan:
    t = await _plan_step_2b()
    return await move_to_next(t)


@pytest.fixture
async def plan_step_4() -> Plan:
    return await _plan_step_4()

async def _plan_step_4() -> Plan:
    t = await _plan_step_3()
    return await move_to_next(t)


@pytest.fixture
async def plan_step_5() -> Plan:
    return await _plan_step_5()

async def _plan_step_5() -> Plan:
    t = await _plan_step_4()
    return await move_to_next(t)


@pytest.fixture
async def plan_step_6() -> Plan:
    return await _plan_step_6()

async def _plan_step_6() -> Plan:
    t = await _plan_step_5()
    return await move_to_next(t)


@pytest.fixture
async def plan_step_7() -> Plan:
    return await _plan_step_7()

async def _plan_step_7() -> Plan:
    t = await _plan_step_6()
    return await move_to_next(t)


@pytest.fixture
async def plan_step_8() -> Plan:
    return await _plan_step_8()

async def _plan_step_8() -> Plan:
    t = await _plan_step_7()
    return await move_to_next(t)


@pytest.fixture
async def plan_step_9() -> Plan:
    return await _plan_step_9()

async def _plan_step_9() -> Plan:
    t = await _plan_step_8()
    return await move_to_next(t)


@pytest.fixture
async def plan_step_10() -> Plan:
    return await _plan_step_10()

async def _plan_step_10() -> Plan:
    t = await _plan_step_9()
    return await move_to_next(t)


@pytest.fixture
async def plan_step_11() -> Plan:
    return await _plan_step_11()

async def _plan_step_11() -> Plan:
    t = await _plan_step_10()
    return await move_to_next(t)

@pytest.fixture
async def task_ready_no_predecessors_or_subtasks() -> Task:
    return await _default_task()

@pytest.fixture
async def default_task():
    return await _default_task()

async def _default_task():
    # Task 'task_101_buy_groceries' has no predecessors or subtasks and is ready
    p = await plan_familly_dinner_with_tasks_saved_in_db()
    t = await p.get_task(task_id="101")
    if len(await t._task_predecessors.get_active_tasks_from_stack()) > 0 or len(await t._subtasks.get_active_tasks_from_stack()) > 0:
        raise(f"Error : Fixture default_task need to be updated")
    if t.state is not TaskStatusList.READY :
        raise(f"Error : Fixture default_task should be ready")
    return t


@pytest.fixture(scope="function")
async def task_ready_all_predecessors_done(plan_step_2b: Plan) -> Task:
    # Task 'task_300_2_2_line_pan' with all predecessors done
    t = await plan_step_2b.get_task(task_id="300.2.2")
    if len(await t._task_predecessors.get_all_tasks_from_stack()) == len(t._task_predecessors.get_done_tasks_from_stack()):
        raise(f"Error : Fixture task_ready_all_predecessors_done need to be updated")
    return t


@pytest.fixture(scope="function")
async def task_ready_all_subtasks_done(plan_step_8: Plan) -> Task:
    # Task 'task_300_1_gather_ingredients' with all subtasks done
    t = await plan_step_8.get_task(task_id="300.1")
    if len(t._subtasks.get_all_tasks_from_stack()) == len(t._subtasks.get_done_tasks_from_stack()):
        raise(f"Error : Fixture task_ready_all_subtasks_done need to be updated")
    return t


@pytest.fixture(scope="function")
async def task_with_mixed_predecessors(plan_step_7: Plan) -> Task:
    # Task 'task_300_6_serve_bread' with some predecessors done and some not
    t = await plan_step_7.get_task(task_id="300.6")
    if len(await t._task_predecessors.get_active_tasks_from_stack()) > 0 and len(await t._task_predecessors.get_active_tasks_from_stack())  < len(await t._task_predecessors.get_all_tasks_from_stack()) :
        raise(f"Error : Fixture task_with_mixed_predecessors need to be updated")
    return t


@pytest.fixture(scope="function")
async def task_with_unmet_predecessors(plan_step_0: Plan) -> Task:
    # Task '300.3.3' has unmet predecessors at plan_step_0
    t = await plan_step_0.get_task(task_id="300.3.3")
    if len(await t._task_predecessors.get_active_tasks_from_stack()) > 0:
        raise(f"Error : Fixture task_with_unmet_predecessors need to be updated")
    return t


@pytest.fixture(scope="function")
async def task_with_ongoing_subtasks(plan_step_0: Plan) -> Task:
    # Task '200' has ongoing subtasks at plan_step_0
    t = await plan_step_0.get_task(task_id="200")
    if t.state != TaskStatusList.IN_PROGRESS_WITH_SUBTASKS:
        raise(f"Error : Fixture task_with_ongoing_subtasks need to be updated")
    return t


@pytest.fixture(scope="function")
async def task_awaiting_preparation(plan_step_0: Plan) -> Task:
    # Task '300.4' is not ready yet at plan_step_0
    t = await plan_step_0.get_task(task_id="300.4")
    if t.state == TaskStatusList.READY:
        raise(f"Error : Fixture task_awaiting_preparation need to be updated")
    return t
