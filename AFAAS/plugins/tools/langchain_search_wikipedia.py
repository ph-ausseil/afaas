from langchain_community.tools.wikipedia.tool import WikipediaQueryRun, WikipediaAPIWrapper

from AFAAS.core.tools.tool_decorator import tool_from_langchain
from AFAAS.core.tools.tool import Tool
import subprocess
from dotenv import load_dotenv
from AFAAS.lib.sdk.logger import AFAASLogger
from AFAAS.lib.sdk.add_api_key import add_to_env_file

LOG = AFAASLogger(name=__name__)


# @tool_from_langchain()
# def query_wikipedia(**kwargs) : 
#     return WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()).arun(**kwargs)


try:
    import wikipedia
except ImportError:
    import subprocess
    LOG.info("wikipedia package is not installed. Installing...")
    subprocess.run(["pip", "install", "wikipedia"])
    LOG.info("wikipedia package has been installed.")

query_wikipedia = Tool.generate_from_langchain_tool(
    tool=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()), 
    #arg_converter=file_search_args,
    categories=["search" , "wikipedia"],
)
