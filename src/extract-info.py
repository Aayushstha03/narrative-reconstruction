import google.genai as genai
from google.genai import types
from dotenv import load_dotenv
import os
import json

def call_gemini_llm(article, prompt):

    event_extraction_schema = {
        "title": "Event Extraction Schema",
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "event": {"type": "string", "description": "Short title or label for the event"},
                "actors": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of people, organizations, or groups involved"
                },
                "time_expression": {
                    "type": "string",
                    "description": "Time or date phrase as it appears in the article"
                },
                "resolved_time": {
                    "type": "string",
                    "format": "date",
                    "description": "Normalized date in YYYY-MM-DD format"
                },
                "location": {
                    "type": ["string", "null"],
                    "description": "Place associated with the event"
                },
                "details": {
                    "type": "string",
                    "description": "Full sentence or two describing the event"
                }
            },
            "required": ["event", "actors", "time_expression", "resolved_time", "details"]
            }
        }


    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    try:
        # The new google-genai expects a single string prompt
        full_prompt = f"{prompt}\n\n{article.get('content', '')}"
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            config=types.GenerateContentConfig(
                response_mime_type = "application/json",
                response_json_schema=event_extraction_schema,
                temperature=0.0,
            ),
            contents=full_prompt
        )
        
        # Try to parse the response as JSON, fallback to text
        try:
            entities = response.text
            if entities.strip().startswith('{') or entities.strip().startswith('['):
                import json as _json
                entities = _json.loads(entities)
        except Exception:
            entities = response.text
        return {"entities": entities}
    except Exception as e:
        print(f"Gemini API error: {e}")
        return {"entities": []}

def main():
    # Load environment variables from .env
    load_dotenv()
    with open('src/data/article_contents.json', 'r', encoding='utf-8') as f:
        articles = json.load(f)

    prompt = """You are an expert in event extraction from Nepali news articles.

    Given the article title, published date, and content below, extract all distinct events or stages.

    For each event, provide these fields:
    - event: a short title or label
    - actors: list of people, organizations, or groups involved
    - time_expression: the original time/date phrase from the article
    - resolved_time: the normalized date (YYYY-MM-DD)
    - location: place associated with the event (if any)
    - details: a full sentence or two describing the event

    Only include events relevant to the article’s main story
    Here is the article metadata and content:
    """

    results = []
    for article in articles:
        print(f"Processing: {article.get('url')}")
        # You can pass the whole article or just the content/title as needed
        response = call_gemini_llm(article, prompt)
        results.append({
            "url": article.get('url'),
            "title": article.get('title'),
            "published_date": article.get('published_date'),
            "entities": response.get('entities', [])
        })

    # Save extracted entities to a new JSON file
    with open('src/data/article_entities.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("Done. Saved to src/article_entities.json")

if __name__ == "__main__":
    main()
