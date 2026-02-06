from fastapi import FastAPI, Request
from .models import Base
from .database import engine
from .router import auth, todos, admin, user
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles 


app = FastAPI()

template = Jinja2Templates(directory="Todo/template")
app.mount("/static", StaticFiles(directory="Todo/static"), name="static")

@app.get("/")
def test(request:Request):
    return template.TemplateResponse("home.html",{"request":request})

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(todos.router)
app.include_router(admin.router)

Base.metadata.create_all(bind=engine)



