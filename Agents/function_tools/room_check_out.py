from ..utils.room_map_utils import room_check_out,room_validation,get_all_room_numbers
from ..database import SessionLocal
from sqlalchemy.orm import session
from ..model import BookRoom,Payment,Customers
from datetime import date
from ..config import CHARGE_PER_DAY_STAY
import random

async def room_checkout_confirmation(room_number:int)->dict:
    """
    This tool must be called before room check out for confirmation.
    returns a message for confirmation of the provided details (e.g., room number, name, phone number, total bill etc.) 
    and ask hoe would the user wants to pay the amount
    parameters :
      room_number : room number of the user
    """
    db = None
    try:
        db:session = SessionLocal()
        if not room_validation(room_number=room_number):
            all_room_numbers = await get_all_room_numbers()
            return {'status':'failed','message':'The room does not exist','available_rooms':all_room_numbers}
        room = db.query(BookRoom).filter(BookRoom.room_number == room_number).first()
        cust_id = room.customer_id
        customer = db.query(Customers).filter(Customers.id == cust_id).first()
        total_bill = (date.today() - customer.check_in_date ).days * CHARGE_PER_DAY_STAY
        return {'status':'waiting for confirmation','message':f'confirm the information. Name {customer.name}, '\
                f'phone number {customer.ph_number} and check in date is {customer.check_in_date}.',
                'query':f'The total bill is {total_bill} how would you like to pay?'}
    except Exception as e:
        return {'status':'failed','message':f'error in room_checkout_confirmation : {e}'}
    finally:
        if db:
            db.close()

async def pay_bill(room_number:int,payment_method:str,amount:int,cust_id:int,db)->dict:
    try:
        random_number = random.randint(0,10)
        if random_number == 5:
            return {'status':'failed','message':f'payment failed! try again'}
        new_payment = Payment(
                amount = amount,
                payment_method = payment_method,
                room_number = room_number,
                customer_id = cust_id
            )
        db.add(new_payment)
        db.commit()
        return {'status':'success'}
    except Exception as e:
        if db:
            db.rollback()
        return {'status':'failed','message':f'error in update_room_in_db : {e}'}

async def update_room_in_db(room_number:int,db,room)->dict:
    try:
        
        if room is None or not room.is_booked:
            return {'status':'not_found','message':'the room was not booked or not found'}
        setattr(room,'is_booked',False)
        setattr(room,'booked_by',None)
        setattr(room,'customer_id',None)
        setattr(room,'check_in_date',None)
        setattr(room,'check_out_date',None)
        #db.add(room)
        db.commit()
        return {'status':'success'}
    except Exception as e:
        if db:
            db.rollback()
        return {'status':'failed','message':f'error in update_room_in_db : {e}'}

async def room_checkout(room_number:int,payment_method:str,amount:int)->dict:
    """A tool for room checkout. returns a failure or success message based on the situation
    Parameters:
        - room_number : room_number of the user. returned from room_checkout_confirmation
        - payment_method : how the user wants to pay (cash,paytm,credit card etc.)
        - amount : the total amount or bill which is being paid

    """
    db = None
    try:
        db = SessionLocal()
        room = db.query(BookRoom).filter(BookRoom.room_number == room_number).first()
        if room is None or not room.is_booked:
            return {'status':'not_found','message':'the room was not booked or not found'}
        payment_status = await pay_bill(
            room_number=room_number,
            payment_method=payment_method,
            amount=amount,
            cust_id=room.customer_id,
            db=db,
        )
        if payment_status.get('status','failed') == 'failed':
            return payment_status
        db.refresh(room)
        room_update_status = await update_room_in_db(room_number=room_number,room=room,db=db)
        if room_update_status.get('status','failed') in ['failed','not_found']:
            return room_update_status
        db.commit()
        await room_check_out(room_number=room_number)
        return {'status':'successful','message':'checkout has been done successfuly.'}
    except Exception as e:
        if db:
            db.rollback()
        return {'status':'failed','message':f'exception occured in room_checkout : {e}'}
    finally:
        if db:
            db.close()



