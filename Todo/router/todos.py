import logging
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Todos
from .auth import get_current_user


router=APIRouter(
    prefix='/todos',
    tags=['todos']
)
logger = logging.getLogger(__name__)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
def write_log(message:str):
    logger.info(message)

db_dependency=Annotated[Session,Depends(get_db)]
user_dependency= Annotated[dict,Depends(get_current_user)]

template = Jinja2Templates(directory="Todo/template")
class TodoRequest(BaseModel):
    title:str = Field(min_length=3, max_length=30)
    description:str = Field(min_length=3)
    priority:int = Field(gt=0)
    complete:bool = Field(default=False)

def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page",status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response

###pages
@router.get("/todo-page")
def render_todo_page(request:Request, db:db_dependency):
    try:
        user= get_current_user(request.cookies.get("access_token"))
        if user is None:
            logger.warning("Attempt to access todo page without valid user")
            return redirect_to_login()
        
        todos=db.query(Todos).filter(Todos.ownerid==user.get("id")).all()
        logger.info("Rendering todo page for user_id=%s with %s todos", user.get("id"), len(todos))
        return template.TemplateResponse("todo.html",{"request":request,"todos":todos, "user":user})
    except Exception as exc:
        logger.error("Failed to render todo page: %s", exc)
        return redirect_to_login()

@router.get("/add-todo-page")
def render_add_todo_page(request:Request):
    try:
        user= get_current_user(request.cookies.get("access_token"))
        if user is None:
            logger.warning("Attempt to access add todo page without valid user")
            return redirect_to_login()
        logger.info("Rendering add todo page for user_id=%s", user.get("id"))
        return template.TemplateResponse("add-todo.html",{"request":request,"user":user})
    except Exception as exc:
        logger.error("Failed to render add todo page: %s", exc)
        return redirect_to_login()
    

@router.get("/edit-todo-page/{todo_id}")
def render_edit_todo_page(request:Request,db:db_dependency,todo_id:int):
    try:
        user= get_current_user(request.cookies.get("access_token"))
        if user is None:
            logger.warning("Attempt to access edit todo page without valid user")
            return redirect_to_login()
        todo=db.query(Todos).filter(Todos.id==todo_id).first()
        logger.info("Rendering edit todo page for user_id=%s todo_id=%s", user.get("id"), todo_id)
        return template.TemplateResponse("edit-todo.html",{"request":request,"user":user,"todo":todo})
    except Exception as exc:
        logger.error("Failed to render edit todo page: %s", exc)
        return redirect_to_login()


### Endpoints
@router.get("/",status_code=status.HTTP_200_OK)
def read_all_todos(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401,detail="Authentication failed")
    todos = db.query(Todos).filter(user.get('id')==Todos.ownerid).all()
    logger.info("Fetched %s todos for user_id=%s", len(todos), user.get("id"))
    return todos

@router.get("/todo/{todo_id}",status_code=status.HTTP_200_OK)
def read_todo(user: user_dependency,db:db_dependency,todo_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,detail="Authentication failed")
    value= db.query(Todos).filter(Todos.ownerid==user["id"]).filter(Todos.id==todo_id).first()
    if value is not None:
        logger.info("Retrieved todo_id=%s for user_id=%s", todo_id, user.get("id"))
        return value
    logger.warning("Todo not found for user_id=%s todo_id=%s", user.get("id"), todo_id)
    raise HTTPException(status_code=404,detail="Todo with this id not found")

@router.post("/create_todo",status_code=status.HTTP_201_CREATED)
def create_todo(user:user_dependency,db:db_dependency, todo_request:TodoRequest,background_tasks:BackgroundTasks):
    if user is None:
        raise HTTPException(status_code=401,detail="Authentication failed")
    todo_modal=Todos(**todo_request.model_dump(),ownerid=user.get('id'))
    background_tasks.add_task(write_log,message=f"Todo {todo_request.title} is created")
    db.add(todo_modal)
    db.commit()
    logger.info("Created todo '%s' for user_id=%s", todo_request.title, user.get("id"))
    return "you successfully added the data"


@router.put("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
def update_todo(user:user_dependency, db:db_dependency,todo_request:TodoRequest,todo_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,detail="Authentication failed")
    todo_model=db.query(Todos).filter(Todos.id==todo_id).filter(Todos.ownerid==user['id']).first()
    if todo_model is None:
        logger.warning("Todo update failed: todo_id=%s not found for user_id=%s", todo_id, user.get("id"))
        raise HTTPException(status_code=404, detail="todo is not found")
    todo_model.title=todo_request.title
    todo_model.description=todo_request.description
    todo_model.priority=todo_request.priority
    todo_model.complete=todo_request.complete

    db.add(todo_model)
    db.commit()
    logger.info("Updated todo_id=%s for user_id=%s", todo_id, user.get("id"))

@router.delete("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(user:user_dependency, db:db_dependency,todo_id:int=Path(gt=0)):
    if user is None:
        HTTPException(status_code=401,detail="Authentication Failed")
    todo_model=db.query(Todos).filter(Todos.id==todo_id).filter(Todos.ownerid==user['id']).first()
    if todo_model is None:
        logger.warning("Todo delete failed: todo_id=%s not found for user_id=%s", todo_id, user.get("id"))
        raise HTTPException(status_code=404, detail="todo is not found")
    db.query(Todos).filter(Todos.id==todo_id).filter(Todos.ownerid==user['id']).delete()
    db.commit()
    logger.info("Deleted todo_id=%s for user_id=%s", todo_id, user.get("id"))

