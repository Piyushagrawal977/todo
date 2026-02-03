from ..main import app
from ..router.todos import get_db
from ..router.auth import get_current_user
from fastapi.testclient import TestClient
from fastapi import status
from ..models import Todos
from .utils import *


app.dependency_overrides[get_db]=override_get_db
app.dependency_overrides[get_current_user]=overrider_get_user

client = TestClient(app)


def test_read_all_authentication(test_todo):
    response = client.get("/")
    assert response.status_code==status.HTTP_200_OK
    # print(response.json())
    # assert response.json() == []

def test_read_one_authenticate(test_todo):
    response = client.get("/todo/1")
    assert response.status_code==status.HTTP_200_OK
    assert response.json()=={
        "title":"Learn FastApi",
        "complete":False,
        "priority":2,
        'description':"python modern framework to connect DB and Frontend Through RestAPI",
        'ownerid':1,
        'id':1
    }

def test_read_authenticate_not_found(test_todo):
    response = client.get("/todo/999")
    assert response.status_code==status.HTTP_404_NOT_FOUND
    assert response.json()=={"detail":"Todo with this id not found"}

def test_create_todo(test_todo):
    request_body={
        'title': "New Todo",
        'complete':False,
        'priority':2,
        'description':"new day",
    }

    response = client.post("/create_todo",json=request_body)
    assert response.status_code==status.HTTP_201_CREATED

    db=TestingSessionLocal()
    modal_todo=db.query(Todos).filter(Todos.id==2).first()
    assert modal_todo.title==request_body['title']
    assert modal_todo.description==request_body['description']
    assert modal_todo.priority==request_body['priority']
    assert modal_todo.complete==request_body['complete']
    # assert modal_todo.title==request_body['title']

def test_update_todo(test_todo):
    request_body={
        'title':'change the title',
        "complete":False,
        'priority':3,
        'description':"move on to the next todo"
    }

    response = client.put("/todo/1",json=request_body)

    assert response.status_code==status.HTTP_204_NO_CONTENT
    db=TestingSessionLocal()
    modal=db.query(Todos).filter(Todos.id==1).first()
    assert modal.title==request_body['title']

def test_update_todo_not_found(test_todo):
    request_body={
        'title':'change the title',
        "complete":False,
        'priority':3,
        'description':"move on to the next todo"
    }

    response = client.put("/todo/999",json=request_body)

    assert response.status_code==status.HTTP_404_NOT_FOUND
    assert response.json()=={"detail":"todo is not found"}

def test_delete_todo(test_todo):
    respone=client.delete("/todo/1")
    assert respone.status_code==status.HTTP_204_NO_CONTENT
    db=TestingSessionLocal()
    modal=db.query(Todos).filter(Todos.id==1).first()
    assert modal is None

def test_delete_todo_not_found(test_todo):
    respone=client.delete("/todo/999")
    assert respone.status_code==status.HTTP_404_NOT_FOUND