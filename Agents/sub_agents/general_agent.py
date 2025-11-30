from google.adk.agents import Agent
from google.adk.tools.function_tool import FunctionTool
from google.adk.models import Gemini
from sqlalchemy.orm import session
from ..utils.utils import retry_config
from ..config import MODEL_NAME
from ..hotel_details import CHARGE_PER_DAY_STAY,BEDS_PER_ROOM
from ..function_tools.about import get_details
from .sub_agent_tools.comfort_requests import comfort_request
from ..function_tools.get_feedback import get_feedback

prebooking_agent = Agent(
    name='general_agent',
    model=Gemini(model=MODEL_NAME,retry_options=retry_config),
    description="you are a helpful assistant for completing guests requests for extra comforts",
    instruction=f"""you are a helpful assistant for completing guests requests for extra comforts
          - if user wants any kind of comfort then you can use comfort_request for request for that comfort
          - if the user reports for some issue or discomfort, then use the get_feedback tool and set the sentiment to urgent
    """,
    tools=[
        FunctionTool(comfort_request),
        FunctionTool(get_feedback)
        ],
)



