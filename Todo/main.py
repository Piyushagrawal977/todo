from fastapi import FastAPI
from .models import Base
from .database import engine
from .router import auth, todos, admin, user

app = FastAPI()
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(todos.router)
app.include_router(admin.router)

Base.metadata.create_all(bind=engine)


