from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from uuid import uuid4
import json
from pathlib import Path
import asyncio

app = FastAPI()

TASK_FILE = Path(__file__).parent / 'tasks.json'

# Ensure file exists
if not TASK_FILE.exists():
    TASK_FILE.write_text(json.dumps({}))


class SearchRequest(BaseModel):
    query: str


class SearchResponse(BaseModel):
    task_id: str
    status: str


class SearchResult(BaseModel):
    task_id: str
    status: str
    result: dict | None = None


# Utility functions
def read_tasks():
    return json.loads(TASK_FILE.read_text())


def write_tasks(data):
    TASK_FILE.write_text(json.dumps(data, indent=2))


# Dummy background task (simulates LLM processing)
async def process_query(task_id: str, query: str):
    await asyncio.sleep(10)  # Simulate delay
    tasks = read_tasks()
    tasks[task_id]['status'] = 'completed'
    tasks[task_id]['result'] = {
        'summary': f"This is a dummy result for query: '{query}'"
    }
    write_tasks(tasks)


@app.post('/search', response_model=SearchResponse)
async def search(req: SearchRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid4())
    tasks = read_tasks()
    tasks[task_id] = {
        'query': req.query,
        'status': 'processing',
        'result': None,
    }
    write_tasks(tasks)

    # Kick off background task
    background_tasks.add_task(process_query, task_id, req.query)

    return {'task_id': task_id, 'status': 'processing'}


@app.get('/search-result/{task_id}', response_model=SearchResult)
async def get_result(task_id: str):
    tasks = read_tasks()
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail='Invalid task ID')

    task = tasks[task_id]
    return {
        'task_id': task_id,
        'status': task['status'],
        'result': task['result'],
    }


@app.get('/')
def hello_world():
    return {'message': 'Hello, World!'}
