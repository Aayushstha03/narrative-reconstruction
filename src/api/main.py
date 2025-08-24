from fastapi import FastAPI
from src.bg_tasks.tasks import sample_task

app = FastAPI()


@app.get('/run-task')
def run_task(duration: int):
    task = sample_task.apply_async(args=[duration])
    return {
        'task_id': task.id,
        'status': 'Task has been started in the background.',
    }


@app.get('/task-status/{task_id}')
def get_task_status(task_id: str):
    task = sample_task.AsyncResult(task_id)
    return (
        {'status': task.state, 'result': task.result}
        if (task.state == 'SUCCESS')
        else {'status': task.state}
    )
