from ..model import BookRoom,Customers
from ..database import SessionLocal
from datetime import date
from ..utils.room_map_utils import (get_room_number,room_check_in,room_validation,get_all_room_numbers,reload_room_map)
from ..config import CHARGE_PER_DAY_STAY
from ..logging import logging



async def book_room_confirmation(check_out_date:str,room_number:int=None)->dict:
    """returns the booking details (eg., room number, floor, check out date and cost) to ask for approval for booking
    required parameters: 
    1. check_out_date : the date when the user wants to check out (format YYYY/MM/DD)
    2. room_number : the room number the user wants to book. It is an optional field if not provided it will choose autometically.
    """
    if room_number and not room_validation(room_number=room_number):
        all_room_numbers = await get_all_room_numbers()
        return {'status':'failed','message':'The room does not exist','available_rooms':all_room_numbers}
    if room_number is None:
        room_number = await get_room_number()
    year,month,day = check_out_date.split('/')
    year,month,day = int(year),int(month),int(day)
    check_out_date = date(year=year,month=month,day=day)
    total_cost = (check_out_date - date.today()).days * CHARGE_PER_DAY_STAY
    return {
            'status':'waiting for approval',
            'message':f'waiting for client confirmation for booking room number {room_number} on the floor {room_number//100}.'\
            f'Total cost {total_cost} and check out date is {check_out_date}'
                }


async def booking_data_entry(name,ph_number,address,check_out_date:str,room_number:int):
    db=None
    try:
        db=SessionLocal()
        check_in_date = date.today()
        total_cost = (check_out_date - date.today()).days * CHARGE_PER_DAY_STAY
        room = db.query(BookRoom).filter(BookRoom.room_number == room_number).first()

        if room is not None and room.is_booked is True:
            await reload_room_map()
            return {'status':'failed','message':'the room is already booked'}
            

        new_customer = Customers(
            name=name,
            ph_number= ph_number,
            address = address,
            room_number = room_number,
            total_bill = 0,
            check_in_date = check_in_date
        )
        
        db.add(new_customer)
        db.commit()
        customer = db.query(Customers).filter(Customers.room_number == room_number).filter(Customers.check_in_date == check_in_date).first()
        if customer is None:
            return {'status':'failed','message':'customer data added but not found again'}
        
        if room is not None:
            setattr(room,'booked_by',name)
            setattr(room,'is_booked',True)
            setattr(room,'check_in_date',check_in_date)
            setattr(room,'check_out_date',check_out_date)
            setattr(room,'customer_id',customer.id)
        else:
            room = BookRoom(
                room_number=room_number,
                is_booked=True,
                booked_by=name,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                customer_id = customer.id
            )
            db.add(room)
        db.commit()
        return {'status':'successful','message':f'Room no. {room_number} in floor {room_number//100} is booked by {name}. and total bill will be {total_cost}'}
    except Exception as e:
        if db:
            db.rollback()
        return {'status':'failed','message':f'Booking error : {str(e)}'}
    finally:
        if db:
            db.close()

async def book_room(name:str,ph_number:str,address:str,check_out_date:str,room_number:int)->dict:
    """Books a room according to room number.
    Parameters for booking a room:
    name : name of the client
    ph_number : phone number with country code
    address : full address
    check_out_date : The date for which the client will check out (e.g., 2023/11/10) 
    room_number : room_number from book_room_confirmation tool return
    """
    
    year,month,day = check_out_date.split('/')
    year,month,day = int(year),int(month),int(day)
    check_out_date = date(year=year,month=month,day=day)
    try:
        booking_status = await booking_data_entry(name=name,ph_number=ph_number,address=address,check_out_date=check_out_date,room_number=room_number)
        if booking_status.get('status',None) == 'failed':
            return booking_status
        await room_check_in(room_number=room_number)
        if booking_status:
            return booking_status
        return {'status':'processing','message':'waiting for confirmation'}
    
    except Exception as e:
        return {'status':'failed','message':f'Booking error : {str(e)}'}





