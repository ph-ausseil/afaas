import json
import requests
import yaml
from pathlib import Path
import click

from autogpt.core.agent import AgentSettings, SimpleAgent
from autogpt.core.runner.client_lib.logging import get_client_logger

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"  # adjust to match your server address and port

print("Press Enter to Test all the end points : \n")

# GET /agents
response = requests.get(f"{BASE_URL}/agents")
print("GET /agents response:", response.json())

# POST /agent
response = requests.post(f"{BASE_URL}/agent")
print("POST /agent response:", response.json())
agent_id = response.json()["agent_id"]

# GET /agent/{agent_id}
response = requests.get(f"{BASE_URL}/agent/{agent_id}")
print(f"GET /agent/{agent_id} response:", response.json())

# POST /agent/{agent_id}/start
# assuming the request body is a JSON object with "message" and "start" keys
start_request_body = {
    "message": "your message here",
    "start": True  # or False
}
response = requests.post(f"{BASE_URL}/agent/{agent_id}/start", json=start_request_body)
print(f"POST /agent/{agent_id}/start response:", response.json())

# POST /agent/{agent_id}/message
# assuming the request body is a JSON object with "message" and "start" keys
message_request_body = {
    "message": "your message here",
    "start": True  # or False
}
response = requests.post(f"{BASE_URL}/agent/{agent_id}/message", json=message_request_body)
print(f"POST /agent/{agent_id}/message response:", response.json())

input("\n\nPress Enter to start AutoGPT\n\n")

def run_auto_gpt_webapp():
   
    """Run the Auto-GPT CLI client."""

    client_logger = get_client_logger()
    client_logger.debug("Getting agent settings")


    response = requests.get(f"{BASE_URL}/agents/")
    response_data = response.json()
    simple_agent_as_dict = response_data.get('agents')[0]

    # Todo : Needs to create a SimpleAgent from a dict
    agent = SimpleAgent.load_from_dict(simple_agent_as_dict)
    print("agent is loaded")


    response = requests.post(f"{BASE_URL}/agent/{agent_id}/start")
    print(response.json())

    user_input : str = ''
    while user_input.lower != 'n' :
        user_input = click.prompt(
            "Should the agent proceed with this ability?",
            default="y",
        )        
        message_request_body = {
            "message": user_input,
            "start": True  # or False
        }
        response = requests.post(f"{BASE_URL}/agent/{agent_id}/message", json=message_request_body)
        print(f"POST /agent/{agent_id}/message response:", response.json())

