from google.adk.agents import Agent
from google.adk.tools.function_tool import FunctionTool
from google.adk.models import Gemini
from sqlalchemy.orm import session
from ..utils.utils import retry_config
from ..config import MODEL_NAME
from ..hotel_details import CHARGE_PER_DAY_STAY,BEDS_PER_ROOM
from ..function_tools.about import get_details
from .sub_agent_tools.prebooking_tool import prebooking_tool
from .sub_agent_tools.cancel_prebooking_tool import cancel_prebooking_confirmation,cancel_prebooking
from .sub_agent_tools.prebooking_to_checkin import check_in_from_prebooking,approval_for_check_in_from_prebooking
from ..function_tools.get_feedback import get_feedback


prebooking_agent = Agent(
    name='prebooking_agent',
    model=Gemini(model=MODEL_NAME,retry_options=retry_config),
    description="you are a helpful assistant for prebooking a room in our hotel",
    instruction=f"""you are a helpful assistant for prebooking a room in our hotel.
    you have the capability of
    1) Prebook a room :
          - Inform the guest that every room is {BEDS_PER_ROOM} beded and every room cost {CHARGE_PER_DAY_STAY} rs. per day stay.
          - if the user agree to book rooms then call the prebooking_tool tool to prebook rooms with appropriate parameters 
          (if date is not in form of yyyy/mm/dd then format it yourself)
          - If the returned status is 'failed' show the user proper reason and try to resolve it if you can't,
            then tell the user to contact the hotel management service directly by providing details usng get_details tool.
          - If the returned status is 'successful' or 'success' show the result (confirmation) to the guest.  
    2) Cancel a prebooking :
          - you must use the cancel_prebooking_confirmation to confirm room number and show the payment requierment if required
          - if user confirms to cancel bookings then use the cancel_prebooking tool with confirmed room numbers to cancel prebooking.
          - show the results
          - ask the user if he wants to provide any feedback or not. If yes then use the get_feedback tool
    3) check in from prebooking :
          - first of all you must use the approval_for_check_in_from_prebooking tool to get approval from guest
          - if user approve then use check_in_from_prebooking to book the rooms
    4) for any work which you can't do reffer to root agent
    """,
    tools=[
        FunctionTool(prebooking_tool),
        FunctionTool(get_details),
        FunctionTool(cancel_prebooking_confirmation),
        FunctionTool(cancel_prebooking),
        FunctionTool(approval_for_check_in_from_prebooking),
        FunctionTool(check_in_from_prebooking)
        ],
)



