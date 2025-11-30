from ..database import SessionLocal
from sqlalchemy.orm import session
from ..model import BookRoom


async def check_room(room_numbers:list[int]):
    """
    provided details about the room numbers which are provided. if booked then booked by whom. if prebookedthn prebooked by whom etc. a checking tool for room.
    returns is it booked, booked by, prebooked by and prebook check in date.
    parameter:
        - room_numbers : room numbers to check. a list of integers
    """
    db=None
    try:
        db=SessionLocal()
        data = []
        for rn in room_numbers:
            room = db.query(BookRoom).filter(BookRoom.room_number == rn).first()
            if room is None:
                info = f"room {rn} is not booked"
            else:
                if room.is_booked and room.prebook_checkin_date :
                    info = f"room {rn} is booked by {room.booked_by} and prebooked by {room.prebooked_by} ,check in date is {room.prebook_checkin_date}"
                elif room.is_booked and not room.prebook_checkin_date:
                    info = f"room {rn} is booked by {room.booked_by} and not prebooked"
                elif room.is_booked and room.prebook_checkin_date :
                    info = f"room {rn} is prebooked by {room.prebooked_by} ,check in date is {room.prebook_checkin_date} and not booked currently"
            data.append(info) 
        return_str = ". ".join(data)
        return {'status':'succeed','message':return_str}   
    except Exception as e:
        return {'status':'failed','message':f'Error in check_room : {e}'}
