from ...model import BookRoom
from ...database import SessionLocal
from datetime import date
from ...hotel_details import CANCELATION_FEE_PER_DAY
from ...function_tools.pay import pay_bill
async def cancel_prebooking_confirmation(name:str,room_numbers:list[int]=None)->dict:
    """
    returns a list of room numbers. and ask the guest for confirmation that room prebooking can be canceled also a minimal cancelation payment is required
    parameters : 
    - name : name of the guest or the provided name while booking
    - room_numbers : a optional field, room numbers for canceling rooms 
    """
    db=None
    try:
        db=SessionLocal()
        rooms = []
        prebooked_date = []
        total_cost = 0
        if room_numbers:
            for room_number in room_numbers:
                room = db.query(BookRoom).filter(BookRoom.room_number==room_number).filter(BookRoom.prebooked_by == name.lower()).first()
                if room is None:
                    return {'status':'failed','message':'room not found'}
                rooms.append(room.room_number)  
                prebooked_date.append(room.prebook_date)   
        else:
            prebooked_rooms = db.query(BookRoom).filter(BookRoom.prebooked_by == name).all()
            for room in prebooked_rooms:
                rooms.append(room.room_number)
        for d in prebooked_date:
            total_cost += abs((date.today() - d).days * CANCELATION_FEE_PER_DAY)
        if total_cost>0:
            return {'status':'waiting for confirmation','message':f"Confirm your room numbers are {rooms}",
                    'payment_required':f"Your canceletion fee : {total_cost} rs. how would you like to pay?"}
        return {'status':'waiting for confirmation','message':f"Confirm your room numbers are {rooms}. yourcancellation fee is 0rs"}
    except Exception as e:
        return {'status':'Error','message':f"cancel_prebooking_confirmation failed due to internal error : {e}"}
    finally:
        if db:
            db.close()
        
async def cancel_prebooking(room_numbers:list,amount:int,payment_method:str=None)->dict:
    """
    This tool cancels prebooking and returns confirmation
    parameters:
    - room_numbers : room numbers to cancel prebooking. after confirmation 
    - amount : the cancelation amount returned from cancel_prebooking_confirmation
    - payment_method : how the user wants to pay the bill . if amount is 0 then do not rquired
    """
    db = None
    try:
        db = SessionLocal()
        formated_room_numbers = '|'.join(str(rn) for rn in room_numbers)
        payment_status = await pay_bill(
            room_numbers=formated_room_numbers,
            payment_method=payment_method,
            amount=amount,
            cust_id=0,
            db=db,
        )
        if payment_status.get('status','failed') == 'failed':
            return payment_status
        for room_number in room_numbers:
            room = db.query(BookRoom).filter(BookRoom.room_number==room_number).first()
            if not room:
                return {"status":"failed","message":f"room no {room_number}  not found in prebooking"}
            room.prebook_checkin_date = None
            room.prebook_date = None
            room.prebooked_by = None
            room.prebooking_ph_number = None
        db.commit()
        return {'status':'successful','message':'prebooking has been canceled'}
    except Exception as e:
        if db:
            db.rollback()
        return {'status':'Error','message':f"cancel_prebooking_confirmation failed due to internal error : {e}"}
    finally:
        if db:
            db.close()







