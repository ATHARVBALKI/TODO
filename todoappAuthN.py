from fastapi import FastAPI, Depends, HTTPException, Header
from typing import Optional
import uvicorn

app = FastAPI(title="My first fastapi app", version="1.0.0")

API_KEY = "todo-secret-key"

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key is None:
        raise HTTPException(
            status_code=401, 
            detail="API key missing",
            headers={"WWW-Authenticate": "API-Key"}
        )
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401, 
            detail="Invalid API key",
            headers={"WWW-Authenticate": "API-Key"}
        )
    return x_api_key

id_counter = 0

todos = []

@app.get("/todos/")
def get_todos():
    return todos

@app.post("/todos/", status_code=201)
def create_todo(title: str, description: str="", completed = False):
    global id_counter
    new_todo = {
        "id" : id_counter,
        "title" : title,
        "description" : description,
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
    return None

@app.put("/todos/{todo_id}", dependencies=[Depends(verify_api_key)])
def update_todo(todo_id: int, title: str = None, description: str = None, completed: bool = None):
    for todo in todos:
        if todo["id"] == todo_id:
            # Update fields only if new values are provided
            if title is not None:
                todo["title"] = title
            if description is not None:
                todo["description"] = description
            if completed is not None:
                todo["completed"] = completed
            return todo
    return None

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    for i, todo in enumerate(todos):
        if(todo["id"] == todo_id):
            todos.pop(i)
            return{f"Deleted successfully {todo_id}"}
    return None

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port = 8000)