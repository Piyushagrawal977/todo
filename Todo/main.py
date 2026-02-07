from fastapi import FastAPI, Request,status
from .models import Base
from .database import engine
from .router import auth, todos, admin, user
from fastapi.staticfiles import StaticFiles 
from fastapi.responses import RedirectResponse


app = FastAPI()


app.mount("/static", StaticFiles(directory="Todo/static"), name="static")

@app.get("/")
def test(request:Request):
    return RedirectResponse(url="/todos/todo-page",status_code=status.HTTP_302_FOUND)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(todos.router)
app.include_router(admin.router)

Base.metadata.create_all(bind=engine)



