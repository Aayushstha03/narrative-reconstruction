from fastapi import FastAPI
from pydantic import BaseModel
import json
from pathlib import Path

app = FastAPI()
DATA_FILE = Path(__file__).parent.parent / 'worker' / 'articles.json'


class Article(BaseModel):
    id: str
    title: str
    timestamp: str


@app.get('/')
def hello_world():
    return {'message': 'Hello, World!'}


def read_articles():
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)


@app.get('/articles', response_model=list[Article])
def get_articles():
    return read_articles()
