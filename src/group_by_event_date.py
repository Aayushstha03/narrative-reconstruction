import json
from collections import defaultdict

# Load the extracted entities
with open('src/data/article_entities.json', 'r', encoding='utf-8') as f:
    articles = json.load(f)

grouped_by_date = defaultdict(list)

for article in articles:
    for entity in article.get('entities', []):
        event_date = entity.get('event_date')
        if event_date:
            grouped_by_date[event_date].append({
                'article_url': article['url'],
                'title': article['title'],
                'published_date': article['published_date'],
                **entity
            })

# Save grouped results
with open('src/data/entities_grouped_by_event_date.json', 'w', encoding='utf-8') as f:
    json.dump(grouped_by_date, f, ensure_ascii=False, indent=2)

print('Done. Saved to src/data/entities_grouped_by_event_date.json')
