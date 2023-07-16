### Some of it might have to be provided by the core

import click
from autogpt.core.agent import AgentSettings, SimpleAgent ### @TODO should work for every Agent
from autogpt.core.runner.client_lib.logging import get_client_logger


def parse_agent_name_and_goals(name_and_goals: dict) -> str:
    parsed_response = f"Agent Name: {name_and_goals['agent_name']}\n"
    parsed_response += f"Agent Role: {name_and_goals['agent_role']}\n"
    parsed_response += "Agent Goals:\n"
    for i, goal in enumerate(name_and_goals["agent_goals"]):
        parsed_response += f"{i+1}. {goal}\n"
    return parsed_response

async def workspace_loader(user_configuration : dict, client_logger, agent_workspace) : 
    """Run the Auto-GPT CLI client."""

    # Step 1. Collate the user's settings with the default system settings.
    agent_settings: AgentSettings = SimpleAgent.compile_settings(
        client_logger,
        user_configuration,
    )

    # Step 2. Get a name and goals for the agent.
    # First we need to figure out what the user wants to do with the agent.
    # We'll do this by asking the user for a prompt.
    user_objective = click.prompt("What do you want Auto-GPT to do?")
    # Ask a language model to determine a name and goals for a suitable agent.
    name_and_goals = await SimpleAgent.determine_agent_name_and_goals(
        user_objective,
        agent_settings,
        client_logger,
    )

    parsed_agent_goals = parse_agent_name_and_goals(name_and_goals)
    print(parsed_agent_goals)
    # Finally, update the agent settings with the name and goals.
    agent_settings.update_agent_name_and_goals(name_and_goals)

    # Step 3. Provision the agent.
    agent_workspace = SimpleAgent.provision_agent(agent_settings, client_logger)
    print("agent is provisioned")
    return agent_workspace


def get_logger_and_workspace(user_configuration: dict):
    client_logger = get_client_logger()
    client_logger.debug("Getting agent settings")

    agent_workspace = (
        user_configuration.get("workspace", {}).get("configuration", {}).get("root", "")
    )
    return client_logger, agent_workspace
