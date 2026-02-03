from sqlalchemy import create_engine,text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from ..database import Base
import pytest
from ..models import Todos, Users
from ..router.auth import bcrypt_context


SQLALCHEMY_DATABASE_URL="sqlite:///./testdb.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread":False},
    poolclass=StaticPool
)

TestingSessionLocal =sessionmaker(autoflush=False,autocommit=False,bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db=TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def overrider_get_user():
    return {'username':"helloji",'id':1,'role':"admin"}

@pytest.fixture
def test_todo():
    todo = Todos(
        title="Learn FastApi",
        complete=False,
        priority=2,
        description="python modern framework to connect DB and Frontend Through RestAPI",
        ownerid=1
    )

    db=TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("Delete from todos;"))
        connection.commit()

@pytest.fixture
def test_user():
    user=Users(
        first_name="hello",
        last_name="ji",
        role="admin",
        user_name="helloji",
        hashed_password=bcrypt_context.hash("123456"),
        phone_number="1234567890",
        email="helloji@gmail.com"
    )
    db=TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("Delete from users;"))
        connection.commit()
    
