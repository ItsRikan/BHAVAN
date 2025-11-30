from ...model import BookRoom,Customers
from ...database import SessionLocal
from datetime import date
from ...utils.room_map_utils import (room_check_in,room_validation_for_booking,reload_room_map,get_n_room_numbers_for_booking)
from ...hotel_details import CHARGE_PER_DAY_STAY
from ...logging import logging




async def book_room_confirmation(check_out_date:str,number_of_rooms:int=None,room_numbers:list[int]=None)->dict:
    """returns the booking details (eg., room number, floor, check out date and cost) to ask for approval for booking
    required parameters: 
    1. check_out_date : the date when the user wants to check out (format YYYY/MM/DD)
    2. Either you provide number_of_rooms or room_numbers
        - number_of_rooms : number of rooms guest wants to book.
        - room_numbers : a list of room numbers the guest wants to book.
    """
    db=None
    try:
        await reload_room_map()
        db = SessionLocal()
        try:
            y, m, d = check_out_date.split('/')
            check_out_date:date = date(int(y), int(m), int(d))
            if check_out_date<date.today():
                return {'status':'failed','message':"check-out date is wrong"}
        except Exception:
            return {'status': 'failed', 'message': 'invalid date format, expected YYYY/MM/DD'}
        
        if (not room_numbers or len(room_numbers)==0) and not number_of_rooms:
            return {'status':'failed','message':'either room number(s) or number of rooms you want needed'}
        elif room_numbers and len(room_numbers)>0 and not number_of_rooms:
            for rn in room_numbers:
                validation_status = room_validation_for_booking(room_number=rn,check_out_date=check_out_date,db=db)
                if validation_status.get('status','failed')== 'failed':
                    return validation_status
        elif number_of_rooms and (not room_numbers or len(room_numbers)==0):
            get_rooms_status = await get_n_room_numbers_for_booking(n=int(number_of_rooms),db=db,check_out_date=check_out_date)
            if get_rooms_status.get('status','failed')=='failed':
                return get_rooms_status
            room_numbers = get_rooms_status['list_of_rooms']
        if number_of_rooms and room_numbers is not None:
            if len(room_numbers)<number_of_rooms:
                return {'status':'succeed','message':f"only {len(room_numbers)} room(s) are available, which are {room_numbers}."}
            
                
            elif len(room_numbers)>number_of_rooms:
                room_numbers = room_numbers[:number_of_rooms]
        total_cost = abs((check_out_date - date.today()).days * CHARGE_PER_DAY_STAY * number_of_rooms)
        return {'status':'waiting for approval','message':f"booking for {number_of_rooms} rooms : {room_numbers} and total cost will be {total_cost} if you check-out on {check_out_date}"}      

    except Exception as e:
        return {'status':'failed','message':f'Booking error : {str(e)}'}
    finally:
        if db:
            db.close()

async def booking_data_entry(name,ph_number,address,check_out_date:date,room_numbers:list[int]):
    db=None
    try:        
        db=SessionLocal()
        check_in_date = date.today()
        total_cost = abs((check_out_date - date.today()).days * CHARGE_PER_DAY_STAY * len(room_numbers))
        room_numbers_formated = '|'.join(str(rn) for rn in room_numbers)
            
        new_customer = Customers(
            name=name.lower(),
            ph_number= ph_number,
            address = address,
            room_numbers = room_numbers_formated,
            total_bill = 0,
            check_in_date = check_in_date
        )
        
        db.add(new_customer)
        db.commit()
        customer = db.query(Customers).filter(Customers.room_numbers == room_numbers_formated).filter(Customers.check_in_date == check_in_date).first()
        if customer is None:
            return {'status':'failed','message':'customer data added but not found again'}
        
        for rn in room_numbers:
            room = db.query(BookRoom).filter(BookRoom.room_number == rn).first()
            if room is None:
                room = BookRoom(
                    customer_id = customer.id,
                    room_number=rn,
                    is_booked=True,
                    booked_by=name.lower(),
                    check_in_date=check_in_date,
                    check_out_date=check_out_date,
                    
                )
                db.add(room)
            else:
                room.customer_id = customer.id
                room.room_number = rn
                room.is_booked = True
                room.booked_by = name.lower()
                room.check_in_date = check_in_date
                room.check_out_date = check_out_date
           
        db.commit()
        return {'status':'successful','message':f'{room_numbers} rooms are booked by {name}. and total bill will be {total_cost}'}
    except Exception as e:
        if db:
            db.rollback()
        return {'status':'failed','message':f'Booking error : {str(e)}'}
    finally:
        if db:
            db.close()

async def book_room(name:str,ph_number:str,address:str,check_out_date:str,room_numbers:list[int])->dict:
    """Books a room according to room number.
    Parameters for booking a room:
    name : name of the client
    ph_number : phone number with country code
    address : full address
    check_out_date : The date for which the client will check out. Format : YYYY/MM/DD
    room_number : room_numbers from book_room_confirmation tool return
    """
    try:
        try:
            y, m, d = check_out_date.split('/')
            check_out_date = date(int(y), int(m), int(d))
            if check_out_date<date.today():
                return {'status':'failed','message':"check-out date is wrong"}
        except Exception:
            return {'status': 'failed', 'message': 'invalid date format, expected YYYY/MM/DD'}
        booking_status = await booking_data_entry(name=name.lower(),ph_number=ph_number,address=address,check_out_date=check_out_date,room_numbers=room_numbers)
        if booking_status.get('status',None) == 'failed':
            return booking_status
        for rn in room_numbers:
            await room_check_in(room_number=rn)
        if booking_status:
            return booking_status
        return {'status':'processing','message':'waiting for confirmation'}
    
    except Exception as e:
        return {'status':'failed','message':f'Booking error : {str(e)}'}


 