from time import sleep
import google.genai as genai
from google.genai import types
from dotenv import load_dotenv
import os
import json


def call_gemini_llm(article, prompt):
    event_extraction_schema = {
        'title': 'Event Extraction Schema',
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'event': {
                    'type': 'string',
                    'description': 'Short title or label for the event',
                },
                'actors': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'People, organizations, or groups directly involved in the event. Do not include generic terms, and actors that do not play a significant role in the event should be excluded.',
                },
                'event_date': {
                    'type': 'string',
                    'format': 'YYYY-MM-DD',
                    'description': 'date of the event occurence, use the published date as a reference for constructing the date if not explicitly mentioned',
                },
                'event_time': {
                    'type': ['string', 'null'],
                    'description': 'time in 24-hour format, or null if unknown',
                },
                'location': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'List of places associated with the event.',
                },
                'details': {
                    'type': 'string',
                    'description': 'A short summary of the event, including role of actors, location, and other relevant details',
                },
            },
            'required': [
                'event',
                'actors',
                'event_date',
                'details',
                'location',
            ],
        },
    }

    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    try:
        # The new google-genai expects a single string prompt
        full_prompt = f'{prompt}\n\n{article.get("content", "")}'
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                response_json_schema=event_extraction_schema,
                temperature=0.0,
            ),
            contents=full_prompt,
        )

        # Try to parse the response as JSON, fallback to text
        try:
            entities = response.text
            if entities.strip().startswith('{') or entities.strip().startswith(
                '['
            ):
                import json as _json

                entities = _json.loads(entities)
        except Exception:
            entities = response.text
        return {'entities': entities}
    except Exception as e:
        print(f'Gemini API error: {e}')
        return {'entities': []}


def main():
    # Load environment variables from .env
    load_dotenv()
    with open(
        'src/data/temp_data/article_contents.json', 'r', encoding='utf-8'
    ) as f:
        articles = json.load(f)

    prompt = """You are an expert in event extraction from Nepali news articles.

    Given the article title, published date, and content below, extract all distinct events. Reply in the same language as the article, Nepali.
    Only return information that is relevant to the event and the main article.
    Here is the article metadata and content:
    """

    results = []
    for article in articles:
        print(f'Processing: {article.get("url")}')
        # Only pass title, content, and published_date
        minimal_article = {
            'title': article.get('title'),
            'published_date': article.get('published_date'),
            'content': article.get('content'),
        }
        response = call_gemini_llm(minimal_article, prompt)
        results.append(
            {
                'title': minimal_article['title'],
                'url': article.get('url'),
                'published_date': minimal_article['published_date'],
                'content': minimal_article['content'],
                'entities': response.get('entities', []),
            }
        )
        sleep(1)

    # Save extracted entities to a new JSON file
    with open(
        'src/data/temp_data/article_entities.json', 'w', encoding='utf-8'
    ) as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print('Done. Saved to src/data/temp_data/article_entities.json')


if __name__ == '__main__':
    main()
