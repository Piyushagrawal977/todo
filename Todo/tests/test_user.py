from .utils import *
from ..router.user import get_current_user,get_db
from ..main import app
from fastapi.testclient import TestClient
from fastapi import status
# import pytest

app.dependency_overrides[get_db]=override_get_db
app.dependency_overrides[get_current_user]=overrider_get_user

client = TestClient(app)



def test__read_user(test_user):
    response=client.get("/user/")
    assert response.status_code==status.HTTP_200_OK
    assert response.json()['user_name']=="helloji"


def test_change_password(test_user):
    response=client.put("/user/change_password",json={"password":"123456","new_password":"helloji"})
    assert response.status_code==status.HTTP_204_NO_CONTENT

def test_change_password_not_found(test_user):
    response=client.put("/user/change_password",json={"password":"mukeshji","new_password":"helloji"})
    assert response.status_code==status.HTTP_401_UNAUTHORIZED
    assert response.json()=={"detail":"Your current password doesn't match"}


def test_change_phone_number(test_user):
    response=client.put("/user/phone_number",params={"phone_number":"1234567892"})
    assert response.status_code==status.HTTP_204_NO_CONTENT