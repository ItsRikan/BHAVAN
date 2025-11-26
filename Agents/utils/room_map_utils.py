from ..hotel_details import NUMBER_OF_ROOMS_PER_FLOOR,NUMBER_OF_FLOORS
from .json_utils import load_json,save_json
from ..database import SessionLocal
from sqlalchemy.orm import session
from ..model import BookRoom
import os
from ..logging import logging
from ..config import (
    ARTIFACT_PATH,
    ROOM_MAP,
)

def room_validation(room_number:int):
    FIRST_ROOM_NUMBER = (NUMBER_OF_FLOORS * 100) + 1
    LAST_ROOM_NUMBER = (NUMBER_OF_FLOORS * 100) + NUMBER_OF_ROOMS_PER_FLOOR
    if not ((FIRST_ROOM_NUMBER<=room_number<=LAST_ROOM_NUMBER) or (1<=room_number%100<=NUMBER_OF_ROOMS_PER_FLOOR)):
        return False
    return True

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
        db.close()




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



async def get_room_number():
    room_map = await initiate_room_map()
    floor = None
    room_num = None
    for i in range(len(room_map)):
        if floor is not None:
            break
        for j in range(len(room_map[i])):
            if not room_map[i][j]:
                floor = i+1
                room_num = j+1
                break
    return ((floor * 100) + room_num)

async def get_all_room_numbers():
    """return all available room numbers"""
    room_numbers = []
    room_map = await initiate_room_map()
    for i in range(len(room_map)):
        for j in range(len(room_map[i])):
            if not room_map[i][j]:
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