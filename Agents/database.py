from sqlalchemy.orm import sessionmaker,declarative_base
from sqlalchemy import create_engine


DB_URL = "sqlite:///./hotel_management_db.db"

engine = create_engine(url=DB_URL,connect_args={'check_same_thread':False})
SessionLocal = sessionmaker(bind=engine,autoflush=False,autocommit=False)
Base = declarative_base()




