from .database import Base,engine
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.function_tool import FunctionTool
from .utils.utils import retry_config
from .utils.room_map_utils import get_all_room_numbers
from .sub_agents.tourist_place_finder import attraction_point_search_agent
from .config import MODEL_NAME,ROOT_AGENT_NAME
from dotenv import load_dotenv
from .function_tools.about import get_details
from .function_tools.get_feedback import get_feedback
from .sub_agents.sub_agent_tools.room_check_out import room_checkout_confirmation,room_checkout
from .sub_agents.prebooking_agent import prebooking_agent
from .sub_agents.booking_agent import booking_agent
from .sub_agents.general_agent import general_agent
from .function_tools.check_room import check_room
load_dotenv()


Base.metadata.create_all(engine)


root_agent = Agent(
    name=ROOT_AGENT_NAME,
    model=Gemini(model=MODEL_NAME,retry_options=retry_config),
    instruction="""you are a helpful assistance for hospitality management of a hotel.
    You have capablity to:
    1) To get all details about the hotel use get_details tools
    2) For available rooms use get_all_room_numbers tool
    3) Take feedback where you feel you need to for improvement of hotel using get_feedback tool
    3) Find attraction point of a location. using attraction_point_search_agent sub agent 
    4) Current booking of  room using booking_agent (Before transfering confirm once, is the user talking about booking or prebooking)
    5) Prebooking of room using prebooking_agent sub agent (Before transfering confirm once, is the user talking about booking or prebooking)
    6) extra comfort request reffer to general_agent
    7) if you want status/check any room then use check_room to get details about that room
    """,
    tools=[
        FunctionTool(get_details),
        FunctionTool(get_all_room_numbers),
        FunctionTool(get_feedback),
        FunctionTool(check_room)
        ],
        sub_agents=[prebooking_agent,booking_agent,general_agent]
)


