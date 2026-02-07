import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Todos
from .auth import get_current_user


router=APIRouter(
    prefix='/admin',
    tags=['admin']
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


@router.get("/todo")
def read_all_todo(user:user_dependency,db:db_dependency):
    if user is None or user['role']!='admin':
        logger.warning("Unauthorized attempt to list all todos by user %s", user.get("id") if user else None)
        raise HTTPException(status_code=401,detail="Unauthorized User")
    todos = db.query(Todos).all()
    logger.info("Admin user_id=%s fetched %s todos", user.get("id"), len(todos))
    return todos

@router.delete("/todo/{todoid}",status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(user:user_dependency,db:db_dependency,todoid:int = Path(gt=0)):
    if user is None or user['role']!='admin':
        logger.warning("Unauthorized attempt to delete todo_id=%s by user %s", todoid, user.get("id") if user else None)
        raise HTTPException(status_code=401,detail="Unauthorized User")
    todo_model= db.query(Todos).filter(todoid==Todos.id).first()
    if todo_model is None:
        logger.warning("Admin user_id=%s attempted to delete missing todo_id=%s", user.get("id"), todoid)
        raise HTTPException(status_code=404, detail="todo is not found")
    db.query(Todos).filter(Todos.id==todoid).delete()
    db.commit()
    logger.info("Admin user_id=%s deleted todo_id=%s", user.get("id"), todoid)
