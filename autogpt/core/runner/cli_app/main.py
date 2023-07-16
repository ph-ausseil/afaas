import click

from autogpt.core.agent import AgentSettings, SimpleAgent 
from autogpt.core.runner.cli_web_app.server.services.agent import workspace_loader , get_logger_and_workspace


async def run_auto_gpt(user_configuration: dict):
    
    # Get the logger and the workspace movec to a function
    # Because almost every API end-point will excecute this piece of code
    client_logger, agent_workspace = get_logger_and_workspace(user_configuration)


    # Get the logger and the workspace moved to a function
    # Because API end-point will treat this as an error & break
    if not agent_workspace : 
        agent_workspace = await workspace_loader(user_configuration, client_logger, agent_workspace)

    # launch agent interaction loop
    agent = SimpleAgent.from_workspace(
        agent_workspace,
        client_logger,
    )

    plan = await agent.build_initial_plan()
    print(parse_agent_plan(plan))

    while True:
        current_task, next_ability = await agent.determine_next_ability(plan)
        print(parse_next_ability(current_task, next_ability))
        user_input = click.prompt(
            "Should the agent proceed with this ability?",
            default="y",
        )
        ability_result = await agent.execute_next_ability(user_input)
        print(parse_ability_result(ability_result))


def parse_agent_plan(plan: dict) -> str:
    parsed_response = f"Agent Plan:\n"
    for i, task in enumerate(plan["task_list"]):
        parsed_response += f"{i+1}. {task['objective']}\n"
        parsed_response += f"Task type: {task['type']}  "
        parsed_response += f"Priority: {task['priority']}\n"
        parsed_response += f"Ready Criteria:\n"
        for j, criteria in enumerate(task["ready_criteria"]):
            parsed_response += f"    {j+1}. {criteria}\n"
        parsed_response += f"Acceptance Criteria:\n"
        for j, criteria in enumerate(task["acceptance_criteria"]):
            parsed_response += f"    {j+1}. {criteria}\n"
        parsed_response += "\n"

    return parsed_response


def parse_next_ability(current_task, next_ability: dict) -> str:
    parsed_response = f"Current Task: {current_task.objective}\n"
    ability_args = ", ".join(
        f"{k}={v}" for k, v in next_ability["ability_arguments"].items()
    )
    parsed_response += f"Next Ability: {next_ability['next_ability']}({ability_args})\n"
    parsed_response += f"Motivation: {next_ability['motivation']}\n"
    parsed_response += f"Self-criticism: {next_ability['self_criticism']}\n"
    parsed_response += f"Reasoning: {next_ability['reasoning']}\n"
    return parsed_response


def parse_ability_result(ability_result) -> str:
    parsed_response = f"Ability: {ability_result['ability_name']}\n"
    parsed_response += f"Ability Arguments: {ability_result['ability_args']}\n"
    parsed_response = f"Ability Result: {ability_result['success']}\n"
    parsed_response += f"Message: {ability_result['message']}\n"
    parsed_response += f"Data: {ability_result['new_knowledge']}\n"
    return parsed_response
