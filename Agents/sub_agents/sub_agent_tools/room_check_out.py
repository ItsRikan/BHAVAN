from ...utils.room_map_utils import room_check_out,room_number_validation,get_all_room_numbers,reload_room_map
from ...database import SessionLocal
from sqlalchemy.orm import session
from ...model import BookRoom,Payment,Customers
from datetime import date
from ...hotel_details import CHARGE_PER_DAY_STAY,CANCELATION_FEE_PER_DAY
from ...function_tools.pay import pay_bill

async def room_checkout_confirmation(room_numbers:list[int])->dict:
    """
    This tool must be called before room check out for confirmation.
    returns a message for confirmation of the provided details (e.g., room number, name, phone number, total bill etc.) 
    and ask hoe would the user wants to pay the amount
    parameters :
      room_number : room number of the user
    """
    db = None
    try:
        await reload_room_map()
        db:session = SessionLocal()
        cust_ids = set()
        for rn in room_numbers:
            room = db.query(BookRoom).filter(BookRoom.room_number == rn).first()
            if (room is None) or (not room.is_booked) or (room.customer_id is None):
                return {'status':'failed','message':'room not found or not booked'}
            cust_ids.add(room.customer_id)
        if len(cust_ids)!=1:
            return {'status':'failed','message':f"{len(cust_ids)} different customer id found :{cust_ids}",
                    "statement":"all booking must be from same customer else check out one by one "}
        cust_id = cust_ids.pop()
        customer = db.query(Customers).filter(Customers.id == cust_id).first()
        total_bill = abs((date.today() - customer.check_in_date ).days * CHARGE_PER_DAY_STAY * len(room_numbers))
        if total_bill==0:
            total_bill = CANCELATION_FEE_PER_DAY * len(room_numbers)
        return {'status':'waiting for confirmation','message':f'confirm the information. Name {customer.name}, '\
                f'phone number {customer.ph_number} and check in date is {customer.check_in_date}.',
                'query':f'The total bill is {total_bill} how would you like to pay?'}
    except Exception as e:
        return {'status':'failed','message':f'error in room_checkout_confirmation : {e}'}
    finally:
        if db:
            db.close()



async def update_room_in_db(room)->dict:
    try:
        if room is None or not room.is_booked:
            return {'status':'not_found','message':'the room was not booked or not found'}
        room.customer_id = None
        room.is_booked = False
        room.booked_by = None
        room.check_in_date = None
        room.check_out_date = None
        return {'status':'success'}
    except Exception as e:
        return {'status':'failed','message':f'error in update_room_in_db : {e}'}

async def room_checkout(room_numbers:list[int],amount:int,payment_method:str='cash')->dict:
    """A tool for room checkout. returns a failure or success message based on the situation
    Parameters:
        - room_number : room_number of the user. returned from room_checkout_confirmation
        - payment_method : how the user wants to pay (cash,paytm,credit card etc.) (If amount is 0, then dont need payment_method)
        - amount : the total amount or bill which is being paid

    """
    db = None
    try:
        db = SessionLocal()
        cust_id = None
        rooms_to_update = []
        for rn in room_numbers:
            room = db.query(BookRoom).filter(BookRoom.room_number == rn).first()
            if room is None or not room.is_booked:
                return {'status':'failed','message':f'room {rn} not found or not booked'}
            if not cust_id:
                cust_id = room.customer_id
            rooms_to_update.append(room)
        payment_status = await pay_bill(
            room_numbers=room_numbers,
            payment_method=payment_method,
            amount=amount,
            cust_id=cust_id,
            db=db,
        )
        if payment_status.get('status','failed') == 'failed':
            return payment_status
        for room in rooms_to_update:
            update_status = await update_room_in_db(room=room)
            if update_status.get('status','failed'):
                db.rollback()
                return update_status
        db.commit()
        for rn in room_numbers:
            await room_check_out(room_number=rn)
        return {'status':'successful','message':'checkout has been done successfuly.'}
    except Exception as e:
        if db:
            db.rollback()
        return {'status':'failed','message':f'exception occured in room_checkout : {e}'}
    finally:
        if db:
            db.close()



