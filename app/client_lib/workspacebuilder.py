### Some of it might have to be provided by the core

from logging import Logger
from pathlib import Path

import click
import yaml

from AFAAS.core.agents import PlannerAgent  # ## TODO should work for every Agent
from AFAAS.lib.sdk.logger import AFAASLogger

DEFAULT_SETTINGS_FILE = str(Path("~/AFAAS/default_agent_settings.yml").expanduser())


async def workspace_loader(user_configuration: dict, LOG: Logger, agent_workspace):
    """Run the Auto-GPT CLI client."""

    # Step 1. Collate the user's settings with the default system settings.
    agent_settings: PlannerAgent.SystemSettings = PlannerAgent.SystemSettings()

    # Step 2. Get a name and goals for the agent.
    # First we need to figure out what the user wants to do with the agent.
    # We'll do this by asking the user for a prompt.

    user_objective = click.prompt("What do you want Auto-GPT to do?")
    # Ask a language model to determine a name and goals for a suitable agent.
    name_and_goals = await PlannerAgent.determine_agent_name_and_goals(
        user_objective,
        agent_settings,
        LOG,
    )

    # parsed_agent_goals = parse_agent_name_and_goals(name_and_goals)
    # print(parsed_agent_goals)
    # # Finally, update the agent settings with the name and goals.
    # agent_settings.update_agent_name_and_goals(name_and_goals)

    # Step 3. Provision the agent.
    agent_workspace = PlannerAgent.provision_agent(agent_settings, LOG)
    print("agent is provisioned")
    return agent_workspace


def get_logger_and_workspace(user_configuration: dict):
    LOG = AFAASLogger(name=__name__)
    LOG.trace("Getting agent settings")

    agent_workspace = (
        user_configuration.get("workspace", {}).get("configuration", {}).get("root", "")
    )
    return LOG, agent_workspace


def get_settings_from_file():
    """
    Current Back-end for setting is a File
    """
    # TODO : Possible Back-End No SQL Database
    settings_file = Path(DEFAULT_SETTINGS_FILE)
    settings = {}
    if settings_file.exists():
        settings = yaml.safe_load(settings_file.read_text())
    return settings
