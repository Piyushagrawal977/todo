import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Users
from .auth import bcrypt_context, get_current_user


router=APIRouter(
    prefix='/user',
    tags=['user']
)
logger = logging.getLogger(__name__)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_current_user)]

class UserVerification(BaseModel):
    password:str
    new_password:str=Field(min_length=6)

@router.get("/",status_code=status.HTTP_200_OK)
def get_user(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized user")
    logger.info("Fetching profile for user_id=%s", user.get("id"))
    return db.query(Users).filter(Users.id==user['id']).first()

@router.put("/change_password",status_code=status.HTTP_204_NO_CONTENT)
def change_password(user:user_dependency,db:db_dependency,user_verfication:UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail='Unauthorized user')
    user_model=db.query(Users).filter(Users.id==user['id']).first()
    if not bcrypt_context.verify(user_verfication.password,user_model.hashed_password):
        logger.warning("Password change failed for user_id=%s: current password mismatch", user.get("id"))
        raise HTTPException(status_code=401, detail="Your current password doesn't match")

    user_model.hashed_password=bcrypt_context.hash(user_verfication.new_password)
    db.add(user_model)
    db.commit()
    logger.info("Password changed successfully for user_id=%s", user.get("id"))

@router.put("/phone_number",status_code=status.HTTP_204_NO_CONTENT)
def update_phone_number(user:user_dependency,db:db_dependency,phone_number:str = Query(min_length=10 , max_length=10, pattern=r"^\d{10}$")):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized user")
    user_model=db.query(Users).filter(Users.id==user['id']).first()
    user_model.phone_number=phone_number
    db.add(user_model)
    db.commit()
    logger.info("Updated phone number for user_id=%s", user.get("id"))
