from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import secrets
import uvicorn

app = FastAPI(title="Todo API with OAuth2", version="1.0.0")

CLIENTS = {
    "service1": "secret123",
    "service2": "secret456"
}

VALID_TOKENS = set()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_client_credentials(client_id: str, client_secret: str):
    return CLIENTS.get(client_id) == client_secret

def verify_token(token: str = Depends(oauth2_scheme)):
    if token not in VALID_TOKENS:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return {"client_id": "authenticated-client"}

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    client_id = form_data.username
    client_secret = form_data.password
    if not verify_client_credentials(client_id, client_secret):
        raise HTTPException(
            status_code=401,
            detail="Incorrect client credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token = secrets.token_urlsafe(32)
    VALID_TOKENS.add(access_token)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 3600
    }
id_counter = 0
todos = []

@app.get("/todos/")
def get_todos():
    return todos

@app.post("/todos/", status_code=201)
def create_todo(title: str, description: str="", completed: bool = False):
    global id_counter
    new_todo = {
        "id": id_counter,
        "title": title,
        "description": description,
        "completed": completed
    }
    todos.append(new_todo)
    id_counter += 1
    return new_todo

@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    for todo in todos:
        if todo["id"] == todo_id:
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.put("/todos/{todo_id}", dependencies=[Depends(verify_token)])
def update_todo(todo_id: int, title: str = None, description: str = None, completed: bool = None):
    for todo in todos:
        if todo["id"] == todo_id:
            if title is not None:
                todo["title"] = title
            if description is not None:
                todo["description"] = description
            if completed is not None:
                todo["completed"] = completed
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    for i, todo in enumerate(todos):
        if todo["id"] == todo_id:
            todos.pop(i)
            return {"message": f"Deleted successfully {todo_id}"}
    raise HTTPException(status_code=404, detail="Todo not found")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
