import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Users



router=APIRouter(
    prefix='/auth',
    tags=['auth']
)
logger = logging.getLogger(__name__)
bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated ='auto')
oAuth2_bearer =OAuth2PasswordBearer(tokenUrl="/auth/token")


SECRET_KEY="Gz4dfR0NkB92JoNnDDgKIlXC4rzPKVN7Gz4dfR0NkB92JoNnDDgKIlXC4rzPKVN7Gz4dfR0NkB92JoNnDDgKIlXC4rzPKVN7"
ALGORITHUM = 'HS256'

 

class UserRequest(BaseModel):
    email:str
    user_name:str
    first_name:str
    last_name:str
    password:str
    role:str
    phone_number:str

class TokenResponse(BaseModel):
    access_token:str
    token_type:str

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

def write_log(message:str):
    logger.info(message)

db_dependency=Annotated[Session,Depends(get_db)]

template = Jinja2Templates(directory="Todo/template")

def create_access_token(username:str,user_id:int,role:str , expires_deltas:timedelta):
    expiries = datetime.now(timezone.utc)+expires_deltas
    encode = { "sub":username,"id":user_id,"role":role ,"exp":expiries}
    return jwt.encode(encode,SECRET_KEY,ALGORITHUM)

def authenticate_user(username:str, password:str, db):
    user = db.query(Users).filter(username==Users.user_name).first()
    if user is None:
        logger.warning("Authentication failed for username '%s': user not found", username)
        return False
    if not bcrypt_context.verify(password,user.hashed_password):
        logger.warning("Authentication failed for username '%s': invalid password", username)
        return False
    logger.info("Authenticated user '%s' successfully", username)
    return user


def get_current_user(token: Annotated[str,Depends(oAuth2_bearer)]):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHUM])
        username:str=payload.get('sub')
        user_id:int= payload.get('id')
        user_role:str=payload.get('role')
        if username is None or user_id is None:
            logger.warning("Token validation failed: missing username or user_id")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate user ")
        return {'username':username,'id':user_id,'role':user_role}
    except Exception as exc:
        logger.warning("Token validation failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate the user ")
    
###Pages
    
@router.get("/login-page")
def render_login_page(request:Request):
    logger.info("Rendering login page")
    return template.TemplateResponse("login.html",{"request":request})

@router.get("/register-page")
def render_register_page(request:Request):
    logger.info("Rendering register page")
    return template.TemplateResponse("register.html",{"request":request})


###Endpoints

@router.post("/create_user", status_code=status.HTTP_201_CREATED)
def create_user(dp: db_dependency,user_request:UserRequest,background_tasks:BackgroundTasks):
    logger.info("Creating user '%s' with role '%s'", user_request.user_name, user_request.role)
    user_model=Users(
        email=user_request.email,
        user_name=user_request.user_name,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        hashed_password=bcrypt_context.hash(user_request.password),
        role=user_request.role,
        is_active=True,
        phone_number=user_request.phone_number
    )
    background_tasks.add_task(write_log,"User created")
    dp.add(user_model)
    dp.commit()
    logger.info("User '%s' created successfully", user_request.user_name)
    
@router.post("/token",response_model=TokenResponse)
def login(formData:Annotated[OAuth2PasswordRequestForm,Depends()],db:db_dependency):
    user= authenticate_user(formData.username,formData.password,db)
    if not user:
        logger.warning("Login failed for '%s'", formData.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="could not validate user ")
    token = create_access_token(user.user_name,user.id,user.role, timedelta(minutes=20))
    logger.info("Issued access token for user '%s'", formData.username)
    return {
        "access_token":token,
        "token_type":"bearer"
    }



