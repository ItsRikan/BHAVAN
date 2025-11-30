from google.adk.tools.google_search_tool import google_search
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types
from dotenv import load_dotenv
from ..instruction import INSTRUCTION_ATTRACTION_POINT_SEARCHER,STRICT_INSTRUCTION
from ..config import MODEL_NAME
from ..utils.utils import retry_config
from ..function_tools.get_feedback import get_feedback
load_dotenv()


attraction_point_search_agent = Agent(
    name = "attraction_point_search_agent",
    model=Gemini(model=MODEL_NAME,retry_options=retry_config),
    instruction=f"{INSTRUCTION_ATTRACTION_POINT_SEARCHER} \n{STRICT_INSTRUCTION}",
    tools=[google_search]
)










