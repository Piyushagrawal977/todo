from .utils import *
from ..router.admin import get_current_user,get_db
from ..main import app
from fastapi.testclient import TestClient
from fastapi import status

app.dependency_overrides[get_db]=override_get_db
app.dependency_overrides[get_current_user]=overrider_get_user

client = TestClient(app)

def test_read__all_todo(test_todo):
    response = client.get("/admin/todo")
    assert response.status_code==status.HTTP_200_OK

def test_delete_todo(test_todo):
    response=client.delete("/admin/todo/1")
    assert response.status_code==status.HTTP_204_NO_CONTENT
    db=TestingSessionLocal()
    modal=db.query(Todos).filter(Todos.id==1).first()
    assert modal is None

def test_delete_todo_not_found(test_todo):
    response=client.delete("/admin/todo/999")
    assert response.status_code==status.HTTP_404_NOT_FOUND
    assert response.json()=={"detail":"todo is not found"}
    