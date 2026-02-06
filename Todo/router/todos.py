from fastapi import APIRouter, Depends, HTTPException,Path,status
from ..models  import Todos
from ..database import  SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from .auth import get_current_user

router=APIRouter(
    prefix='/todos',
    tags=['todos']
)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session,Depends(get_db)]
user_dependency= Annotated[dict,Depends(get_current_user)]

class TodoRequest(BaseModel):
    title:str = Field(min_length=3, max_length=30)
    description:str = Field(min_length=3)
    priority:int = Field(gt=0)
    complete:bool = Field(default=False)

@router.get("/",status_code=status.HTTP_200_OK)
def read_all_todos(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401,detail="Authentication failed")
    return db.query(Todos).filter(user.get('id')==Todos.ownerid).all()

@router.get("/todo/{todo_id}",status_code=status.HTTP_200_OK)
def read_todo(user: user_dependency,db:db_dependency,todo_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,detail="Authentication failed")
    value= db.query(Todos).filter(Todos.ownerid==user["id"]).filter(Todos.id==todo_id).first()
    if value is not None:
        return value
    raise HTTPException(status_code=404,detail="Todo with this id not found")

@router.post("/create_todo",status_code=status.HTTP_201_CREATED)
def create_todo(user:user_dependency,db:db_dependency, todo_request:TodoRequest):
    if user is None:
        raise HTTPException(status_code=401,detail="Authentication failed")
    print("user",user)
    todo_modal=Todos(**todo_request.model_dump(),ownerid=user.get('id'))
    db.add(todo_modal)
    db.commit()
    return "you successfully added the data"


@router.put("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
def update_todo(user:user_dependency, db:db_dependency,todo_request:TodoRequest,todo_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,detail="Authentication failed")
    todo_model=db.query(Todos).filter(Todos.id==todo_id).filter(Todos.ownerid==user['id']).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="todo is not found")
    todo_model.title=todo_request.title
    todo_model.description=todo_request.description
    todo_model.priority=todo_request.priority
    todo_model.complete=todo_request.complete

    db.add(todo_model)
    db.commit()

@router.delete("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(user:user_dependency, db:db_dependency,todo_id:int=Path(gt=0)):
    if user is None:
        HTTPException(status_code=401,detail="Authentication Failed")
    todo_model=db.query(Todos).filter(Todos.id==todo_id).filter(Todos.ownerid==user['id']).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="todo is not found")
    db.query(Todos).filter(Todos.id==todo_id).filter(Todos.ownerid==user['id']).delete()
    db.commit()

