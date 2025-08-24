import time
from datetime import datetime
from zoneinfo import ZoneInfo
import psycopg
import os


db_config = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
}

nepal_timezone = ZoneInfo("Asia/Kathmandu")  

def scrape_article():
    print("Fetching article...")
    time.sleep(1)

    now = datetime.now(nepal_timezone)
    timestamp = int(now.timestamp())  
    title = f"Sample Article Fetched at {now.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    content = f"This is a sample article content generated at {now.strftime('%Y-%m-%d %H:%M:%S %Z')}."
    url = f"https://example.com/article/{timestamp}"

    print(f"Fetched article titled: '{title}' with URL: {url}")
    return title, content, url, now

def save_to_db(title: str, content: str, url: str, published_at: datetime):
    try:
        with psycopg.connect(
            **db_config
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO articles (title, content, url, published_at)
                    VALUES (%s, %s, %s, %s)
                """, (title, content, url, published_at))
                conn.commit()
        print("Article saved to DB.")
    except Exception as e:
        print(f"Error saving to DB: {e}")


if __name__ == "__main__":
    while True:
        title, content, url, published_at = scrape_article()
        save_to_db(title, content, url, published_at)
        time.sleep(10)
