import asyncio
import uuid
from datetime import datetime, timezone
import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / 'articles.json'


async def scraper_loop():
    if not DATA_FILE.exists():
        DATA_FILE.write_text('[]')

    while True:
        article = {
            'id': str(uuid.uuid4()),
            'title': f'Scraped Article at {datetime.now(timezone.utc).strftime("%H:%M:%S")}',
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }

        articles = json.loads(DATA_FILE.read_text())
        articles.append(article)
        DATA_FILE.write_text(json.dumps(articles, indent=2))
        print(f'[Scraper] Added: {article["title"]}')
        await asyncio.sleep(10)


if __name__ == '__main__':
    asyncio.run(scraper_loop())
