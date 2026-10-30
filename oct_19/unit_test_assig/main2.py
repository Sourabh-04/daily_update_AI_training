from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


my_app = FastAPI()

class Task(BaseModel):
    id : int
    title: str
    status: str

task_input =[]


@my_app.get("/task")
def get_task():
    return task_input


@my_app.get("/task/{id}")
def get_task(id:int):
    for task in task_input:
        if task.id == id:
            return task
    raise HTTPException(
        status_code=404,
        detail="Task not found"
    )


@my_app.post("/task")
def create_task(input: Task):
    task_input.append(input)
    return { "message": "Task created successfully" }


@my_app.put("/task/{id}")
def update_task(id:int,updated_task:Task):
    for index,t in enumerate(task_input):
        if t.id == id:

            task_input[index] = updated_task
            return { "message": "Task updated successfully" }
    return { "message": "Task not updated successfully" }

@my_app.delete("/task/{id}")
def delete_task(id:int):
    for index,t in enumerate(task_input):
        if t.id == id:
            del task_input[index]
            return { "message": "Task deleted successfully" }
        return { "message": "Task not deleted successfully" }