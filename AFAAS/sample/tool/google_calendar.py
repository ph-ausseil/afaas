
from llama_hub.tools.google_calendar import GoogleCalendarToolSpec
from llama_index.bridge.langchain import Tool
from llama_index.tools.function_tool import FunctionTool

from AFAAS.core.tools.tool_decorator import tool_from_langchain
from AFAAS.lib.sdk.logger import AFAASLogger

LOG = AFAASLogger(name=__name__)

tool_spec = GoogleCalendarToolSpec()
tool_list: list[FunctionTool] = tool_spec.to_tool_list()

for llamatool in tool_list:
    langchaintool: Tool = llamatool.to_langchain_tool()

    # Create a unique class name using the name of the langchaintool
    class_name = f"Adapted{langchaintool.name.capitalize()}Tool"

    # Dynamically create a new class with a unique name
    AdaptedToolClass = type(class_name, (langchaintool.__class__,), {})

    # Apply the tool_from_langchain decorator to the dynamically created class
    AdaptedToolClass = tool_from_langchain()(AdaptedToolClass)

    LOG.debug(f"Tool : {AdaptedToolClass.__name__} created")

# load_data: Load the upcoming events from your calendar
# create_event: Creates a new Google Calendar event
# get_date: Utility for the Agent to get todays date
