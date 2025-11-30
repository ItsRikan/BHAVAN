from typing import Literal
from ...hotel_details import LIST_OF_EXTRA_COMFORTS,NUMBER_OF_ROOMS_PER_FLOOR,NUMBER_OF_FLOORS
from ...database import SessionLocal
from sqlalchemy.orm import session
from ...model import BookRoom

async def comfort_request(room_number:int,request_for:list[str],quantity:list[int]):
    """Helps to book extra comforts. (e.g, towel, pillow)\
    parameters :
        - room_number : room number of the guest 
        - request_for : list of comfort name. (e.g, [towel, pillow])
        - quantity : quantity corrosponding to the comfort
    length of both parameters must be equal. If guest do not provide quantity for any product then place 1
    """
    try:
        if len(request_for)!=len(quantity):
            return {'status':'failed','message':'length of the parameters are not same'}
        room_validation_status = await varify_room_number(room_number=room_number)
        if room_validation_status.get('status','failed') == 'failed':
            return room_validation_status
        for rq in request_for:
            if rq not in LIST_OF_EXTRA_COMFORTS:
                return {'ststus':'failed','message':f'we only provides {LIST_OF_EXTRA_COMFORTS}'}
        
        return {'status':'succeed','message':'requested extra comforts will be delevered as soon as possible'}
    except Exception as e:
        return {'status':'failed','message':f'Error in comfort_request : {str(e)}'}
        
async def varify_room_number(room_number:int):
    db=None
    try:
        db=SessionLocal()
        FIRST_ROOM_NUMBER = 101
        LAST_ROOM_NUMBER = (NUMBER_OF_FLOORS * 100) + NUMBER_OF_ROOMS_PER_FLOOR
        if not ((FIRST_ROOM_NUMBER<=room_number<=LAST_ROOM_NUMBER) or (1<=room_number%100<=NUMBER_OF_ROOMS_PER_FLOOR)):
            return {'status':'failed','message':f"Invalid room : {room_number} does not exists"}
        room = db.query(BookRoom).filter(BookRoom.room_number == room_number).first()
        if room is None or not room.is_booked:
            return {'status':'failed','message':'room is not booked'}
        return {'status':'succeed'}
    except Exception as e:
        return {'status':'failed','message':f'Error in comfort_request/varify_room_number : {str(e)}'}