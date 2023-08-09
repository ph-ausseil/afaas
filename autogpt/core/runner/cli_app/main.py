import click

from autogpt.core.agent import BaseAgentSettings, SimpleAgent
from autogpt.core.runner.client_lib.logging import get_client_logger
from autogpt.core.runner.client_lib.parser import (
    parse_ability_result,
    parse_agent_plan,
    parse_next_ability,
)


async def run_auto_gpt(user_configuration: dict):
    """Run the Auto-GPT CLI client."""

    client_logger = get_client_logger()
    client_logger.debug("Getting agent settings")

    # Step 1. Collate the user's settings with the default system settings.
    agent_settings: BaseAgentSettings = SimpleAgent.compile_settings(
        client_logger,
        user_configuration,
    )
    import uuid
    user_id = uuid.UUID('a1621e69-970a-4340-86e7-778d82e2137b')
    agent_settings.user_id = user_id

    # NOTE : Real world scenario, this user_id will be passed as an argument
    agent_dict_list = SimpleAgent.get_agentsetting_list_from_memory(user_id=user_id,logger=client_logger)

    agent_from_list = None
    agent_from_memory = None
    # NOTE : This is a demonstration
    # In our demonstration we will instanciate the first agent of a given user if it exists
    if agent_dict_list:
        client_logger.debug(f"User {user_id} has {len(agent_dict_list)} agents.") 
        agent_id = agent_dict_list[0]['agent_id']

        client_logger.debug(f"Loading agent {agent_id} from get_agentsetting_list_from_memory") 
        agent_settings.update_agent_name_and_goals(agent_dict_list[0])
        agent_from_list = SimpleAgent.get_agent_from_settings(
            agent_settings=agent_settings,
            logger=client_logger,
        )

        client_logger.debug(f"Loading agent {agent_id} from get_agent_from_memory") 
        agent_from_memory = SimpleAgent.get_agent_from_memory(agent_settings = agent_settings, agent_id=agent_id, user_id=user_id,logger=client_logger)

        client_logger.debug(f"Comparing agents from agent list and get_agent_from_memory")   
        if str(agent_from_memory._configuration) == str(agent_from_list._configuration):
            client_logger.debug(f"Agents from agent list and get_agent_from_memory are equal")
        else:
            client_logger.debug(f"Agents from agent list and get_agent_from_memory are different")
            client_logger.debug(f"Agents from agent list : {agent_from_list.agent_id}")
            client_logger.debug(f"Agents from get_agent_from_memory : {agent_from_memory.agent_id}")
    
    # NOTE : We continue our tests with the agent from the memory as it more realistic

    agent = agent_from_memory
    #if not agent_workspace:  # We don't have an agent yet.
    if not agent :  # We don't have an agent matching this ID

        # Step 2. Get a name and goals for the agent.
        DEMO = True
        # First we need to figure out what the user wants to do with the agent.
        if DEMO:
            # We'll use a default objective for the demo.
            name_and_goals = {'agent_name': 'FactoryBuilderTest', 
                              'agent_role': 'An automated engineering expert AI, specializing in settling factories in new countries.', 
                              'agent_goals': ['Provide a step-by-step guide on how to build a plant.', 
                                              'Ensure compliance with local regulation', 
                                              'Identification & selection of partners.', 
                                              'Follow implementation untill completion',
                                                'Ensure realization meet quality standards.']}
        else : 
            # We'll do this by asking the user for a prompt.
            user_objective = click.prompt("What do you want Auto-GPT to do? (We will make Pancakes for our tests...)")
            # Ask a language model to determine a name and goals for a suitable agent.
            name_and_goals = await SimpleAgent.determine_agent_name_and_goals(
                user_objective,
                agent_settings,
                client_logger,
            )
        #print(parse_agent_name_and_goals(name_and_goals))
        # Finally, update the agent settings with the name and goals.
        agent_settings.update_agent_name_and_goals(name_and_goals)
        agent_settings.load_root_values()

        # Step 3. Create the agent.
        # TODO : Create a single method that create an agent & the workspace 
        agent_id = SimpleAgent.create_agent(agent_settings, client_logger)

        # agent_id = SimpleAgent.create_agent_in_memory(
        #     agent_settings, client_logger, user_id=user_id
        # )
        agent_settings.agent.agent_id = agent_id
        agent_settings.agent_id = agent_id
        # client_logger.debug(f"3 - Created agent with ID {agent_id}")
        # client_logger.debug(f"3 - Now building the workspace")
        # agent_workspace = SimpleAgent.provision_agent(agent_settings, client_logger)
        # client_logger.debug(f"3 - Workspace built")

        # Step 4. Load the agent.
        # NOTE : There are currently two way to instanciate an Agent, this need to be rationalized
        client_logger.debug(f"Created agent with ID {agent_id}")
        agent = SimpleAgent.get_agent_from_settings(
            agent_settings=agent_settings,
            logger=client_logger,
        )


    # launch agent interaction loop
    print("agent is loaded")
    plan = await agent.build_initial_plan()
    print(parse_agent_plan(plan))

    while True:
        result = await agent.determine_next_ability(plan)
        current_task, next_ability = result
        print(parse_next_ability(current_task, next_ability))
        user_input = click.prompt(
            "Should the agent proceed with this ability?",
            default="y",
        )
        ability_result = await agent.execute_next_ability(user_input)
        print(parse_ability_result(ability_result))
