import random
from ..model import Payment
from sqlalchemy.orm import session
async def pay_bill(room_numbers:list[int],payment_method:str,amount:int,cust_id:int,db:session)->dict:
    try:
        random_number = random.randint(0,10)
        if random_number == 5:
            return {'status':'failed','message':f'payment failed! try again'}
        formated_room_numbers = '|'.join(str(rn) for rn in room_numbers)
        new_payment = Payment(
                amount = amount,
                payment_method = payment_method,
                room_numbers = formated_room_numbers,
                customer_id = cust_id
            )
        db.add(new_payment)
        db.commit()
        return {'status':'success'}
    except Exception as e:
        if db:
            db.rollback()
        return {'status':'failed','message':f'error in update_room_in_db : {e}'}