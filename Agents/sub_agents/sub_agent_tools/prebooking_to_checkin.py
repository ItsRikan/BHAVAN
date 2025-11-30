from ...model import BookRoom,Customers
from ...database import SessionLocal
from datetime import date
#from ...utils.room_map_utils import room_validation
from typing import Optional
from ...hotel_details import CHARGE_PER_DAY_STAY
from ...utils.room_map_utils import room_check_in,reload_room_map
from sqlalchemy.orm import session


async def approval_for_check_in_from_prebooking(name:str,check_out_date:str,room_numbers:list[int]=None)->dict:
    """
    returns the room numbers and total bill to get approval from the guest
    parameters:
    - name : name of the guest or the provided name while booking
    - room_numbers : a optional field, room numbers for check in rooms . should be in form of list of integers
    - check_out_date : when the guest wants to check out. format YYYY/MM/DD
    """
    try:
        await reload_room_map()
        try:
            y, m, d = check_out_date.split('/')
            check_out_date = date(int(y), int(m), int(d))
            if check_out_date<date.today():
                return {'status':'failed','message':"check-out date is wrong"}
        except Exception:
            return {'status': 'failed', 'message': 'invalid date format, expected YYYY/MM/DD'}
        db=SessionLocal()
        
        rooms = []
        if room_numbers:
            for room_number in room_numbers:
                room = db.query(BookRoom).filter(BookRoom.room_number==room_number).first()
                if room is None:
                    return {'status':'failed','message':'room not found'}
                rooms.append(room.room_number) 
        else:
            prebooked_rooms = db.query(BookRoom).filter(BookRoom.prebooked_by == name.lower()).all()
            for room in prebooked_rooms:
                rooms.append(room.room_number)
        total_bill = abs((check_out_date - date.today()).days * CHARGE_PER_DAY_STAY * len(rooms))
        return {'status':'waiting for confirmation','message':f"Confirm your room numbers are {rooms} and your total bill will be {total_bill}"}
    except Exception as e:
        return {'status':'Error','message':f"cancel_prebooking_confirmation failed due to internal error : {e}"}
    finally:
        if db:
            db.close()


async def booking_data_entry(name:str,ph_number:str,address:str,check_out_date:str,room_numbers:list[int],db:session):
    try:
        try:
            y, m, d = check_out_date.split('/')
            check_out_date = date(int(y), int(m), int(d))
            if check_out_date<date.today():
                return {'status':'failed','message':"check-out date is wrong"}
        except Exception:
            return {'status': 'failed', 'message': 'invalid date format, expected YYYY/MM/DD'}
        check_in_date = date.today()
        total_cost = abs((check_out_date - check_in_date).days * CHARGE_PER_DAY_STAY * len(room_numbers))
        room_numbers_format = '|'.join(str(r) for r in room_numbers)
        new_customer = Customers(
            name=name.lower(),
            ph_number= ph_number,
            address = address,
            room_numbers = room_numbers_format,
            total_bill = 0,
            check_in_date = check_in_date
        )
        db.add(new_customer)
        db.commit()
        customer = db.query(Customers).filter(Customers.room_numbers == room_numbers_format).filter(Customers.check_in_date == check_in_date).first()
        if customer is None:
            return {'status':'failed','message':'customer data added but not found again'}
        for room_number in room_numbers:
            room = db.query(BookRoom).filter(BookRoom.room_number==room_number).first()
            if room.is_booked and room.prebook_checkin_date > date.today():
                return {'status':'failed','message':'your check in date is not today'}
            if room.is_booked and room.check_out_date>=date.today():
                return {'status':'failed','message':"can't provide the room is booked. may be bug in code"}
            room.customer_id = customer.id
            room.is_booked = True
            room.booked_by = room.prebooked_by
            room.check_in_date = date.today()
            room.check_out_date = check_out_date
            room.prebook_checkin_date = None
            room.prebook_date = None
            room.prebooked_by = None
            room.prebooking_ph_number = None
            await room_check_in(room_number)
        db.commit()
        return {'status':'successful','message':f'Room no. {room_numbers} is booked by {name}. and total bill will be {total_cost}'}
    except Exception as e:
        if db:
            db.rollback()
        return {'status':'failed','message':f'Booking error : {str(e)}'}
    






async def check_in_from_prebooking(name:str,ph_number:str,address:str,check_out_date:str,room_numbers:list[int]):
    """
    returns a list of room numbers total bill. and ask the guest for confirmation to check in
    parameters : 
    - name : name of the guest or the provided name while booking
    - ph_number : phone number of the guest with country code
    - address : address of the guest
    - check_out_date : the date the guest wants to check out
    - room_numbers : a optional field, room numbers for canceling rooms 
    """
    db = None
    try:
        db = SessionLocal()
        return await booking_data_entry(name=name,ph_number=ph_number,address=address,check_out_date=check_out_date,room_numbers=room_numbers,db=db)
    except Exception as e:
        if db:
            db.rollback()
        return {'status':'failed','message':f'Booking error : {str(e)}'}
    finally:
        if db:
            db.close()




