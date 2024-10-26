import pytest
from autogpt.agents.agent import (
    PlannerAgent,
    PlannerAgentConfiguration,
    PlannerAgentSettings,
)
from autogpt.models.command_registry import CommandRegistry

from AFAAS.configs.config import AIProfile, Config
from AFAAS.lib.task.task import Task


@pytest.fixture
def memory_json_file(config: Config):
    was_memory_backend = config.memory_backend

    config.memory_backend = "json_file"
    memory = get_memory(config)
    memory.clear()
    yield memory

    config.memory_backend = was_memory_backend


@pytest.fixture
def dummy_agent(config: Config, llm_provider, memory_json_file):
    command_registry = CommandRegistry()

    ai_profile = AIProfile(
        ai_name="Dummy PlannerAgent",
        ai_role="Dummy Role",
        ai_goals=[
            "Dummy Task",
        ],
    )

    agent_prompt_config = PlannerAgent.default_settings.prompt_config.copy(deep=True)
    agent_prompt_config.use_functions_api = config.openai_functions
    agent_settings = PlannerAgentSettings(
        name=Agent.default_settings.name,
        description=Agent.default_settings.description,
        ai_profile=ai_profile,
        config=AgentConfiguration(
            fast_llm=config.fast_llm,
            smart_llm=config.smart_llm,
            use_functions_api=config.openai_functions,
            plugins=config.plugins,
        ),
        prompt_config=agent_prompt_config,
        history=Agent.default_settings.history.copy(deep=True),
    )

    agent = PlannerAgent(
        settings=agent_settings,
        llm_provider=llm_provider,
        command_registry=command_registry,
        legacy_config=config,
    )

    return agent
