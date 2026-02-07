# FastAPI Practice Project

This repository currently contains three FastAPI apps:

1. `book.py` - an in-memory book API.
2. `books2.py` - a book API with request validation.
3. `Todo/` - a todo management API with authentication, user/admin routes, SQLite, SQLAlchemy, and Alembic.

## Implemented So Far

### Book API (`book.py`)
- List all books.
- Fetch a single book by title.
- Filter books by category.
- Filter books by author (with optional category endpoint variant).
- Add, update, and delete books in memory.

### Book API v2 (`books2.py`)
- `Book` class-based data model.
- `BookRequest` request validation using Pydantic fields.
- Endpoints to:
  - list all books,
  - read by `book_id`,
  - filter by rating,
  - create a new book with auto-generated id.

### Todo App (`Todo/`)
- SQLAlchemy + SQLite setup in `Todo/database.py`.
- Models in `Todo/models.py`:
  - `Users` (email, username, names, role, hashed password, active flag, phone number)
  - `Todos` (title, description, priority, completion, owner id)
- Main app wiring in `Todo/main.py` with routers:
  - `auth`
  - `user`
  - `todos`
  - `admin`

#### Authentication (`Todo/router/auth.py`)
- User registration: `POST /auth/create_user`
- Token login (OAuth2 password flow): `POST /auth/token`
- JWT token generation/validation
- Password hashing with `passlib` + `bcrypt`

#### User Routes (`Todo/router/user.py`)
- `GET /user/` - get current user profile
- `PUT /user/change_password` - change current user password
- `PUT /user/phone_number` - update current user phone number

#### Todo Routes (`Todo/router/todos.py`)
- `GET /` - list current user todos
- `GET /todo/{todo_id}` - get one todo for current user
- `POST /create_todo` - create todo for current user
- `PUT /todo/{todo_id}` - update current user todo
- `DELETE /todo/{todo_id}` - delete current user todo

#### Admin Routes (`Todo/router/admin.py`)
- `GET /admin/todo` - list all todos (admin only)
- `DELETE /admin/todo/{todoid}` - delete any todo (admin only)

#### Web UI (Jinja Templates)
- Templates in `Todo/template`
- Static assets in `Todo/static`
- Page routes:
  - `GET /` - home page
  - `GET /auth/login-page`
  - `GET /auth/register-page`
  - `GET /todos/todo-page`
  - `GET /todos/add-todo-page`
  - `GET /todos/edit-todo-page/{todo_id}`
- Page auth behavior:
  - Todo pages require the `access_token` cookie.
  - Missing or invalid tokens redirect to `/auth/login-page`.
  - The login page sets the cookie after `POST /auth/token`.

#### Database Migration
- Alembic migration added `phone_number` to `users`:
  - `Todo/alembic/versions/189beca754e9_create_phone_number_for_user_column.py`

## Dependencies

All dependencies are listed in `requirements.txt` (FastAPI, SQLAlchemy, Alembic, python-jose, passlib, uvicorn, and others).

## Run the Apps

```bash
pip install -r requirements.txt

# App 1
uvicorn book:app --reload

# App 2
uvicorn books2:app --reload

# Todo app (run from Todo folder)
cd Todo
uvicorn main:app --reload
```

Open the UI:
```text
http://127.0.0.1:8000/
```

## Current Status

- Core auth + role-based todo management is implemented.
- Database models and migration setup are in place.
- Initial test scaffold exists in `Todo/tests/test_todo.py` and can be expanded.
