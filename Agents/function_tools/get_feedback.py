from typing import Literal
from ..database import SessionLocal
from sqlalchemy.orm import session
from ..model import Feedback


async def insert_feedback(feedback:str,sentiment:Literal['positive','negative']):
    db=None
    try:
        db:session = SessionLocal()
        new_feedback = Feedback(feedback=feedback,sentiment=sentiment)
        db.add(new_feedback)
        db.commit()
    except:
        if not db:
            db.rollback()
    finally:
        db.close()


async def get_feedback(feedback:str,sentiment:Literal['positive','negative'])->dict:
    """
    feedback : feedback of the user
    sentiment : sentiment of the feedback ['positive','negative']
    """
    try:
        if feedback and sentiment:
            await insert_feedback(feedback=feedback,sentiment=sentiment)
            return {'status':'successful','message':'thanks for your feedback'}
        return {'status':'no feedback'}
    except Exception as e:
        return {'status':'failed','message':f'feedback tool problem : {e}'}