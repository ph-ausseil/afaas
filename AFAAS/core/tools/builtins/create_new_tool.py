from __future__ import annotations

import importlib
import os
import re
import json
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from AFAAS.interfaces.agent.main import BaseAgent

from AFAAS.lib.utils.json_schema import JSONSchema

from AFAAS.core.tools.tool_decorator import SAFE_MODE, tool
from AFAAS.interfaces.tools.base import AbstractTool
from AFAAS.lib.sdk.logger import AFAASLogger
from AFAAS.lib.task.task import Task

# Tool may need to be moved to a pipeline
# Get Specifications
# Run a prompt strategy
# Write a file
# Install
# Test
# Loop ?

@tool(
    name="create_function",
    description="This function can create a Python function based on a specific JSON object that describes the desired functionality, including the required imports.",
    parameters={
        "type": "object",
        "properties": {
            "function_description": {
                "type": "object",
                "description": "This parameter receives a JSON object that describes the function you want to create. It must respect the following JSON Schema:",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the function to be created",
                    },
                    "description": {
                        "type": "string",
                        "description": "A brief description of what the function does",
                    },
                    "packages": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "A list of required package to be imported",
                    },
                    "imports": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "A list of required Python modules to import (ex : from package import module)",
                    },
                    "new_config_keys": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "key": {
                                    "type": "string",
                                    "description": "The key name to be added; in the format TOOL_NAMEOFUNCTION_NAMEOFKEY",
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Description of the new  key",
                                },
                            },
                            "required": ["key", "description"],
                        },
                        "description": "A list of envirnmental variable that must be accessible via os.ENVIRON, ideal to store API_KEY, configuration & credentials. ",
                    },
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["object"]},
                            "properties": {
                                "type": "object",
                                "description": "A description of the parameters and their types",
                            },
                            "required": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "A list of required parameters",
                            },
                        },
                        "required": ["type", "properties"],
                    },
                },
                "required": ["name", "parameters"],
            }
        },
        "required": ["function_description"],
    },
)
def create_new_tool(function_description, task : Task, agent: BaseAgent):
    # try:
    #     function_description = json.loads(function_description_json)
    # except json.JSONDecodeError:
    #     raise ValueError("Invalid JSON format for function_description")

    # Validate function name and description
    function_name = function_description.get('name', '')
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', function_name):
        raise ValueError("Invalid function name")


    # Import statements
    imports = "\n".join(

        f"install_and_import_package('module')\nimport {package}" for package in function_description["packages"]
    )

    imports += "\n".join(

        f"install_and_import_package('module')\nimport {module}" for module in function_description["imports"]
    )
    # Adding new config keys
    new_config_keys = "\n    ".join(
        f"ensure_api_key(key= '{key['key']}' , api_name= '{{key['key']}}')"
        for key in function_description.get("new_config_keys", [])
    )

    # Function parameters
    parameters = ", ".join(function_description["parameters"]["required"])

    # Function body
    body = f"""@tool(
    name='{function_description['name']}'
    description='{function_description['description']}'
    parameters={
        function_description["parameters"]
    }
    category="generated_by_framework"
    )
async def {function_description['name']}({parameters} , task : Task, agent: BaseAgent):
    {new_config_keys}
    """

    # Combining everything
    code = f"""from __future__ import annotations

from AFAAS.lib.sdk.add_api_key import install_and_import_package, ensure_api_key
from AFAAS.core.tools.tool_decorator import tool
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from AFAAS.interfaces.agent.main import BaseAgent

from AFAAS.core.tools.tool_decorator import SAFE_MODE, tool
from AFAAS.interfaces.tools.base import AbstractTool
from AFAAS.lib.sdk.logger import AFAASLogger
from AFAAS.lib.task.task import Task
from AFAAS.prompts.routing import RoutingStrategyConfiguration

LOG = AFAASLogger(name=__name__)

{imports}

{new_config_keys}

{body}
    """

    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Path for the new Python file
    file_path = os.path.join(current_directory, function_description["name"] + ".py")

    # Write the Python code to the file
    with open(file_path, "w") as file:
        file.write(code)

    # Load the module
    spec = importlib.util.spec_from_file_location(
        function_description["name"], file_path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return code


    DefaultToolRegistry.write_and_load_module_in_afaas(
        module_name= function_description["name"] , code = code
    )
