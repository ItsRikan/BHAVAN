from ...model import BookRoom
from ...database import SessionLocal
from datetime import date
from ...utils.room_map_utils import get_n_room_number_for_prebooking,reload_room_map


async def prebooking_tool(number_of_rooms:int,booked_by:str,check_in_date:str,prebooking_phone_number:str):
    """
    This tool can prebook a room
    parameters:
       - number_of_rooms : number of rooms the guest wants to book.
       - booked_by : name of the guest
       - check_in_date : when will the guest check in
       - prebooking_phone_number : phone number of the guest (with country code)
    """
    db = None
    try:
        await reload_room_map()
        db = SessionLocal()        
        try:
            y, m, d = check_in_date.split('/')
            requested = date(int(y), int(m), int(d))
            if requested<date.today():
                return {'status':'failed','message':"check-in date is wrong"}
        except Exception:
            return {'status': 'failed', 'message': 'invalid date format, expected YYYY/MM/DD'}
        get_room_response = await get_n_room_number_for_prebooking(prebooking_check_in_date=requested,n=number_of_rooms,db=db)
        if get_room_response.get('status','failed') == 'failed':
            return get_room_response
        room_numbers = get_room_response['list_of_rooms']
        # Extra validation not required for this case
        # for room_number in room_numbers:
        #     if not room_validation(room_number=room_number):
        #         return {'status':'failed','message':'room does not exists'}
        if number_of_rooms>len(room_numbers):
            return {'status':'succeed','message':f"only have {len(room_numbers)} rooms : {room_numbers}"}
        for room_number in room_numbers:
            room = db.query(BookRoom).filter(BookRoom.room_number==room_number).first()
            if room is not None:
                if room.check_out_date and room.check_out_date >= requested:
                    raise BufferError("wrong room taken")
                room.prebook_checkin_date = requested
                room.prebook_date = date.today()
                room.prebooked_by = booked_by.lower()
                room.prebooking_ph_number = prebooking_phone_number
            else:
                new_room = BookRoom(
                    room_number = room_number,
                    is_booked = False,
                    booked_by = None,
                    check_in_date=None,
                    check_out_date = None,
                    prebook_checkin_date = requested,
                    prebook_date =date.today(),
                    prebooked_by = booked_by.lower(),
                    prebooking_ph_number=prebooking_phone_number,
                    customer_id = None,
                )
                db.add(new_room)
        db.commit()
        return {'status':'successful','message':f'your room numbers are {room_numbers}'}       
    except Exception as e:
        if db:
            db.rollback()
        return {'status':'failed','message':f"Error in updateing roombook database : {e}"}   
    finally:
        if db:
            db.close()    
