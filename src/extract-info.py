from time import sleep
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
            "event_date": {
                "type": "string",
                "format": "date",
                "description": "date in YYYY-MM-DD format"
            },
            "event_time": {
                "type": ["string", "null"],
                "pattern": "^([01]\\d|2[0-3]):([0-5]\\d):([0-5]\\d)$",
                "description": "time in 24-hour format, or null if unknown"
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
        "required": ["event", "actors", "time_expression", "event_date", "details"]
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

    Given the article title, published date, and content below, extract all distinct events.
    २०८२ साउन १२ गतेको सोमबार थियो. Using this fact, construct the dates mentioned in the article. Use the nepali calendar date format (YYYY-MM-DD). Please pay extra attention to the dates mentioned in the article, and construct them based on the published date and reference fact date.
    
    Here is the article metadata and content:
    """
    
    # For each event, provide these fields:
    # - event: a short title or label
    # - actors: list of people, organizations, or groups involved
    # - time_expression: the original date/time phrase from the article
    # - event_date: the date (YYYY-MM-DD), using the published_date, identify the date the event occurred in if it's not explicitly mentioned, like day before is one day before the published date.
    # - event_time: the time (24-hour format), use cues like morning, afternoon, evening, to create sample times as well.
    # - location: place associated with the event (if any)
    # - details: a full sentence or two describing the event

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
        sleep(2)

    # Save extracted entities to a new JSON file
    with open('src/data/article_entities.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("Done. Saved to src/article_entities.json")

if __name__ == "__main__":
    main()
