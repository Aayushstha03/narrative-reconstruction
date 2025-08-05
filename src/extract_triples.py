from time import sleep
import google.genai as genai
from google.genai import types
import os
import json


def call_gemini_llm(article, prompt):
    event_extraction_schema = {
        'title': 'News RDF Triples Extraction Schema',
        'type': 'array',
        'description': 'Each item is an RDF triple for the event or fact extracted from the news article.',
        'items': {
            'type': 'object',
            'properties': {
                'subject': {
                    'type': 'object',
                    'description': 'A schema.org entity acting as the subject of the triple. Must be a named entity with a valid schema.org type.',
                    'properties': {
                        '@type': {
                            'type': 'string',
                            'description': 'A valid schema.org type, e.g., Person, Organization, Event, Place, etc.',
                        },
                        'name': {
                            'type': 'string',
                            'description': 'Name or label for the subject.',
                        },
                        'id': {
                            'type': 'string',
                            'description': 'Unique ID or URI if known.',
                        },
                        'additionalProperties': {
                            'description': 'Other properties matching schema.org for the type.',
                            'type': 'object',
                        },
                    },
                    'required': ['@type'],
                },
                'predicate': {
                    'type': 'string',
                    'description': "A valid schema.org property that describes the relation such that the subject's type has this property and the object is of the type expectedby this property according to schema.org definitions, e.g., schema:participant, schema:location, schema:organizer, schema:object.",
                },
                'object': {
                    'type': 'object',
                    'description': 'A schema.org entity acting as the object of the triple, OR a literal value if appropriate. Must be a named entity with a valid schema.org type.',
                    'properties': {
                        '@type': {
                            'type': ['string', 'null'],
                            'description': 'A valid schema.org type if the object is an entity; null if literal.',
                        },
                        'name': {
                            'type': ['string', 'null'],
                            'description': 'Name or label for the object.',
                        },
                        'id': {
                            'type': ['string', 'null'],
                            'description': 'Unique ID or URI if known.',
                        },
                        'value': {
                            'type': ['string', 'number', 'null'],
                            'description': 'Literal value if the object is not an entity.',
                        },
                        'additionalProperties': {
                            'description': 'Other properties matching schema.org for the type.',
                            'type': 'object',
                        },
                    },
                    'required': [],
                },
                'time_expression': {
                    'type': 'string',
                    'description': 'The raw time phrase as it appears in the article.',
                },
                '_date': {
                    'type': 'string',
                    'format': 'date',
                    'description': 'Normalized date in YYYY-MM-DD format.',
                },
                'time': {
                    'type': ['string', 'null'],
                    'pattern': '^([01]\\d|2[0-3]):([0-5]\\d):([0-5]\\d)$',
                    'description': 'Time in 24-hour format or null if not specified.',
                },
                'details': {
                    'type': 'string',
                    'description': 'A short natural language sentence describing this triple or the context.',
                },
            },
            'required': [
                'subject',
                'predicate',
                'object',
                'time_expression',
                '_date',
                'details',
            ],
        },
    }

    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    try:
        # The new google-genai expects a single string prompt
        full_prompt = f'{prompt}\n\n{article.get("content", "")}'
        response = client.models.generate_content(
            model='gemini-2.0-flash',
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
                entities = json.loads(entities)
        except Exception:
            entities = response.text
        return {'entities': entities}
    except Exception as e:
        print(f'Gemini API error: {e}')
        return {'entities': []}


def main():
    # Load environment variables from .env
    with open('src/data/article_contents.json', 'r', encoding='utf-8') as f:
        articles = json.load(f)

    prompt = """You are an information extraction system designed to extract structured facts from news articles and represent them as RDF triples using schema.org types and properties, for the main purpose of building a knowledge graph.

        Task:  
        From the given news text, extract all significant facts as RDF triples.

        Rules:  
        - Keep the triples values/name  and details exactly as the original text, don't translate it to english.
        - Subjects and objects must be specific named entities with a valid schema.org type.
        - Subjects and objects can never be common noun/phrases, events, primitive types, and adjective phrases. 
        - Use only schema.org properties for predicates.  
        - Don't translate the language, keep it exactly the same.
        - Each triple must include:
        - subject: a schema.org entity with @type, name, id if possible, and any extracted properties.
        - predicate: a valid schema.org property that logically matches its subject and object types.
        - object: a schema.org entity if appropriate, or a literal value if the object is just text or a number.

        Additional instructions:  
      
        - Do not use vague or overly generic types (like Thing) if a more precise type exists.
        - Use the same ID and name for any entity that appears under different names but refers to the same real-world thing.
        - Only include a triple if the information is precise enough to be meaningful. Skip vague, speculative, or redundant statements.
        - Do not repeat the same fact more than once.
        - For each triple, also include:
        - time_expression: the raw date or time phrase from the news text.
        - _date: the normalized date in YYYY-MM-DD format if available.
        - time: the normalized time in HH:MM:SS 24-hour format, or null if unknown.
        - details: a short natural language sentence describing the fact in context.

        Quality control:  
        - After forming each triple, check that it makes sense semantically and is valid RDF using schema.org logic i.e. predicate must be a property of the subject's type and object should be of type expected by the property..  
        - Remove any triple that does not make sense.

        Output:  
        - Return only valid JSON that matches the provided JSON Schema.
        - Do not include any extra explanation or text — only the JSON array.

        Here is the article metadata and content:

    """
    #   - If the fact describes an action or event (e.g., leaving, finding, handing over), always model the action as a separate `Event` entity, not as the subject or object directly.

    results = []
    for article in articles:
        print(f'Processing: {article.get("url")}')

        response = call_gemini_llm(article, prompt)
        results.append(
            {
                'url': article.get('url'),
                'title': article.get('title'),
                'published_date': article.get('published_date'),
                'entities': response.get('entities', []),
            }
        )
        sleep(2)

    # Save extracted entities to a new JSON file
    with open('src/data/article_triples.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print('Done. Saved to src/article_triples.json')


if __name__ == '__main__':
    main()
