from fastapi import APIRouter, Depends, HTTPException,Path,status
from ..models  import Todos
from ..database import  SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from .auth import get_current_user


router=APIRouter(
    prefix='/admin',
    tags=['admin']
)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_current_user)]


@router.get("/todo")
def read_all_todo(user:user_dependency,db:db_dependency):
    if user is None or user['role']!='admin':
        raise HTTPException(status_code=401,detail="Unauthorized User")
    return db.query(Todos).all()

@router.delete("/todo/{todoid}",status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(user:user_dependency,db:db_dependency,todoid:int = Path(gt=0)):
    if user is None or user['role']!='admin':
        raise HTTPException(status_code=401,detail="Unauthorized User")
    todo_model= db.query(Todos).filter(todoid==Todos.id).first()
    if todo_model is None:
        raise HTTPException(status_code=401, detail="todo is not found")
    db.query(Todos).filter(Todos.id==todoid).delete()
    db.commit()