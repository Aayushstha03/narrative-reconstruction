from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg
import os

app = FastAPI()

db_config = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
}


class Article(BaseModel):
    article_id: int
    title: str
    content: str
    url: str
    published_at: str


@app.get('/articles/', response_model=Article)
def get_article_by_url(url: str):
    try:
        with psycopg.connect(**db_config) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT article_id, title, content, url, published_at
                    FROM articles WHERE url = %s
                """,
                    (url,),
                )
                row = cur.fetchone()
                if row is None:
                    raise HTTPException(
                        status_code=404, detail='Article not found'
                    )
                article = Article(
                    article_id=row[0],
                    title=row[1],
                    content=row[2],
                    url=row[3],
                    published_at=row[4].isoformat(),
                )
                return article
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
