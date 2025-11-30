from ..hotel_details import NUMBER_OF_ROOMS_PER_FLOOR,NUMBER_OF_FLOORS
from .json_utils import load_json,save_json
from ..database import SessionLocal
from sqlalchemy.orm import session
from ..model import BookRoom
from datetime import date
import os
from ..logging import logging
from ..config import (
    ARTIFACT_PATH,
    ROOM_MAP,
)

def room_number_validation(room_number:int):
    try:
        FIRST_ROOM_NUMBER = 101
        LAST_ROOM_NUMBER = (NUMBER_OF_FLOORS * 100) + NUMBER_OF_ROOMS_PER_FLOOR
        if not ((FIRST_ROOM_NUMBER<=room_number<=LAST_ROOM_NUMBER) or (1<=room_number%100<=NUMBER_OF_ROOMS_PER_FLOOR)):
            return {'status':'failed','message':f"Invalid room : {room_number} does not exists"}
        return {'status':'succeed'}
    except Exception as e:
        return {'status':'failed','message':f"Error in room_number_validation : {str(e)}"}

async def initiate_room_map():
    try:
        if os.path.exists(os.path.join(ARTIFACT_PATH,ROOM_MAP)):
            return await load_json(os.path.join(ARTIFACT_PATH,ROOM_MAP))
        else:
            room_map = [[False for i in range(NUMBER_OF_ROOMS_PER_FLOOR)] for j in range(NUMBER_OF_FLOORS)]
            await save_json(room_map,os.path.join(ARTIFACT_PATH,ROOM_MAP))
            return room_map
    except Exception as e:
        logging.error(f"Error initializing room map: {str(e)}")
        room_map = [[False for i in range(NUMBER_OF_ROOMS_PER_FLOOR)] for j in range(NUMBER_OF_FLOORS)]
        await save_json(room_map,os.path.join(ARTIFACT_PATH,ROOM_MAP))
        return room_map



async def reload_room_map():
    db = None
    try:
        db:session=SessionLocal()
        booked_room_list = db.query(BookRoom).filter(BookRoom.is_booked == True).all()
        room_map = [[False for i in range(NUMBER_OF_ROOMS_PER_FLOOR)] for j in range(NUMBER_OF_FLOORS)]
        for rooms in booked_room_list:
            room_no = rooms.room_number
            floor = (room_no // 100) - 1
            room_num = (room_no % 100) - 1
            room_map[floor][room_num] = True
        await save_json(room_map,os.path.join(ARTIFACT_PATH,ROOM_MAP))
    except Exception:
        pass
    finally:
        if db:
            db.close()

async def get_all_room_numbers():
    """return all available room numbers"""
    room_numbers = []
    room_map = await initiate_room_map()
    for i in range(len(room_map)):
        for j in range(len(room_map[i])):
            number =  ((i + 1) * 100) + (j + 1)  
            room_numbers.append(number)
    return room_numbers



async def room_check_in(room_number:int):
    try:
        assert type(room_number)==int
        floor = (room_number//100) - 1
        room_num = (room_number%100) - 1
        room_map = await initiate_room_map()
        room_map[floor][room_num] = True
        logging.debug("room checked in")
        await save_json(room_map,os.path.join(ARTIFACT_PATH,ROOM_MAP))
        logging.debug("room checked in saved")
    except: 
        raise NotImplementedError('something went wrong in room check out map')

async def room_check_out(room_number:int):
    try:
        assert type(room_number)==int
        floor = (room_number//100) - 1
        room_num = (room_number%100) - 1
        room_map = await initiate_room_map()
        room_map[floor][room_num] = False
        await save_json(room_map,os.path.join(ARTIFACT_PATH,ROOM_MAP))
    except: 
        raise NotImplementedError('something went wrong in room check out map')
    
def room_validation_for_booking(room_number:int,check_out_date:date,db:session):
    try:
        FIRST_ROOM_NUMBER = 101
        LAST_ROOM_NUMBER = (NUMBER_OF_FLOORS * 100) + NUMBER_OF_ROOMS_PER_FLOOR
        if not ((FIRST_ROOM_NUMBER<=room_number<=LAST_ROOM_NUMBER) or (1<=room_number%100<=NUMBER_OF_ROOMS_PER_FLOOR)):
            return {'status':'failed','message':f"Invalid room : {room_number} does not exists"}
        room = db.query(BookRoom).filter(BookRoom.room_number == room_number).first()
        if room is None:
            return {'status':'succeed'}
        if room.prebook_checkin_date and room.prebook_checkin_date < check_out_date:
            return {'status':'failed','message':f"room number {room_number} is prebooked"}
        return {'status':'succeed'}
    except Exception as e:
        return {'status':'failed','message':f"Error in room_validation_for_booking : {str(e)}"}

async def get_n_room_numbers_for_booking(n:int,db:session,check_out_date:date):
    try:
        available_rooms = await get_all_room_numbers()
        refined = []
        for rn in available_rooms:
            room = db.query(BookRoom).filter(BookRoom.room_number==rn).first()
            if room is None:
                refined.append(rn)
            else:
                if room.prebook_checkin_date and room.prebook_checkin_date < check_out_date:
                    continue
                if room.is_booked:
                    continue
                refined.append(rn)
            if len(refined)>=n:
                return {'status':'success','list_of_rooms':refined}
        return {'status':'success','list_of_rooms':refined,'message':f'currently we can provide you {len(refined)} rooms. other rooms are booked'}

    except Exception as e:
        return {'status':'failed','message':f"Error in get_n_room_numbers_for_booking : {str(e)}"}




async def get_n_room_number_for_prebooking(db:session,prebooking_check_in_date:date,n:int=1)->list:
    """
    Returns n number of free rooms which can be book.
    prebooking_check_in_date -> the date the guest will check in.date object
    number_of_roooms -> number of free rooms you want
    """
    try:
        room_numbers =await get_all_room_numbers()
        refined = []

        for rn in room_numbers:
            room = db.query(BookRoom).filter(BookRoom.room_number==rn).first()
            if room is None:
                refined.append(rn)
            else:
                if room.check_out_date and room.check_out_date >= prebooking_check_in_date:
                    continue
                if room.prebook_date and room.prebook_date <= prebooking_check_in_date:
                    continue
                refined.append(rn)
            if len(refined)>=n:
                return {'status':'success','list_of_rooms':refined}
        return {'status':'succeed','list_of_rooms':refined}
    except Exception as e:
        return {'status':'failed','message':f'Error in get_n_room_numbers : {e}'}



