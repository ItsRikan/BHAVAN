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
from .function_tools.room_check_in import book_room,book_room_confirmation
from .function_tools.get_feedback import get_feedback
from .function_tools.room_check_out import room_checkout_confirmation,room_check_out

load_dotenv()


Base.metadata.create_all(engine)


root_agent = Agent(
    name=ROOT_AGENT_NAME,
    model=Gemini(model=MODEL_NAME,retry_options=retry_config),
    instruction="""you are a helpful assistance for hospitality management of a hotel.
    You have capablity to:
    1) To get all details about the hotel use get_details tools
    2) For available rooms use get_all_room_numbers tool
    3) Find attraction point of a location. using attraction_point_search_agent tool 
    provide the name of the location and you can get the nearest tourist points 
    [Note : If no location is mentioned or user says current location use the get_details tool to find the hotel location]
    4)  Can book room using the book_room tool.
            - (You must follow this step) Call the book_room_confirmation tool with check_out_date and room_number if provided. 
              and ask for approval based on the returned data. if the user wants to change any info in this step, 
              call the confirmation tool again with new info.
            - If the user approve it then call the book_room tool to booke the room and show the response based on the returned info
            - If the user denied it ask the user for a feedback then call the get_feedback tool analysis the sentiment and get user problem or feedback
    5) Can check out a client. use the room_checkout_confirmation tool to confirm the user and ask for payment methid.
            - If the user response is confirmed then called the room_check_out
            - Else ask the user again
            - If still user denied for confirming the info then ask for direct contact with hotel manager and provide the contact number using get_details tools
    """,
    tools=[
        AgentTool(attraction_point_search_agent),
        FunctionTool(get_details),
        FunctionTool(get_all_room_numbers),
        FunctionTool(book_room_confirmation),
        FunctionTool(book_room),
        FunctionTool(get_feedback),
        FunctionTool(room_checkout_confirmation),
        FunctionTool(room_check_out)

        ]
)


