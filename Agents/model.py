from .database import Base
from sqlalchemy import Column,String,Integer,Boolean,Date,DateTime,ForeignKey

class BookRoom(Base):
    __tablename__ = 'room_bookng'
    id = Column(Integer,primary_key=True,index=True)
    room_number = Column(Integer)
    is_booked = Column(Boolean,default=False)
    booked_by = Column(String(50))
    check_in_date = Column(Date)
    check_out_date = Column(Date)
    customer_id = Column(Integer,ForeignKey('customers.id'))

class Customers(Base):
    __tablename__ = 'customers'
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String(100))
    ph_number = Column(String(14))
    address = Column(String(100))
    room_number = Column(Integer,ForeignKey('room_bookng.room_number'))
    total_bill = Column(Integer)
    check_in_date = Column(Date)
    
class Payment(Base):
    __tablename__ = 'payment'
    id = Column(Integer,primary_key=True,index=True)
    amount = Column(Integer)
    payment_method = Column(String(20))
    room_number = Column(Integer)
    customer_id = Column(Integer,ForeignKey('customers.id'))   


class SpaSlot(Base):
    __tablename__ = 'spatable'
    id = Column(Integer,primary_key=True,index=True)
    is_booked = Column(Boolean,default=False)
    booked_by = Column(String(50))
    check_in_time = Column(DateTime)
    stay_time = Column(Integer)

class RoomPreBooking(Base):
    __tablename__ = 'prebooking'
    id = Column(Integer,primary_key=True,index=True)
    floor = Column(Integer)
    room_number = Column(Integer)
    is_booked = Column(Boolean,default=False)
    booked_by = Column(String(50))
    check_in_date = Column(Date)
    check_out_date = Column(Date)

class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(Integer,primary_key=True,index=True)
    feedback = Column(String(500))
    sentiment = Column(String(10))


