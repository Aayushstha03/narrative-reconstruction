from fastapi import FastAPI
from ..tasks.example_task import add

app = FastAPI()


@app.get('/')
def hello_world():
    return {'message': 'Hello, World!'}


@app.get('/add')
def trigger_add(a: int, b: int):
    task = add.delay(a, b)  # Enqueue the task asynchronously
    return {'task_id': task.id}
