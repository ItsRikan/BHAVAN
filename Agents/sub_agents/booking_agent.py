from google.adk.agents import Agent
from google.adk.tools.function_tool import FunctionTool
from google.adk.models import Gemini
from ..utils.utils import retry_config
from ..config import MODEL_NAME
from ..hotel_details import CHARGE_PER_DAY_STAY,BEDS_PER_ROOM
from ..function_tools.about import get_details
from .sub_agent_tools.room_check_in import book_room,book_room_confirmation
from .sub_agent_tools.room_check_out import room_checkout,room_checkout_confirmation



booking_agent = Agent(
    name='booking_agent',
    model=Gemini(model=MODEL_NAME,retry_options=retry_config),
    description="you are a helpful assistant for on time booking a room in our hotel",
    instruction=f"""you are a helpful assistant for on time booking a room in our hotel.
    you have the capability of
    1) book room using the book_room tool.
            - (You must follow this step) Call the book_room_confirmation tool with check_out_date and room_number if provided. 
              and ask for approval based on the returned data. if the user wants to change any info in this step, 
              call the confirmation tool again with new info.
            - If the user approve it then call the book_room tool to booke the room and show the response based on the returned info
            - If the user denied it ask the user for a feedback then call the get_feedback tool analysis the sentiment and get user problem or feedback
    2) check out a client or cancelation of a current booked room. use the room_checkout_confirmation tool to confirm the user and ask for payment method.
            - If the user response is confirmed then called the room_check_out
            - Else ask the user again
            - If still user denied for confirming the info then ask for direct contact with hotel manager and provide the contact number using get_details tools
    """,
    tools=[
        FunctionTool(book_room_confirmation),
        FunctionTool(book_room),
        FunctionTool(room_checkout),
        FunctionTool(room_checkout_confirmation),

        ],
)



