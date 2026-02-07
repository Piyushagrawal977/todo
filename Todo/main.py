import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from .database import engine
from .models import Base
from .router import admin, auth, todos, user


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


app = FastAPI()


app.mount("/static", StaticFiles(directory="Todo/static"), name="static")

@app.get("/")
def test(request:Request):
    logger.info("Redirecting root request to /todos/todo-page")
    return RedirectResponse(url="/todos/todo-page",status_code=status.HTTP_302_FOUND)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(todos.router)
app.include_router(admin.router)

Base.metadata.create_all(bind=engine)



