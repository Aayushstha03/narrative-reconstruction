import json
from collections import defaultdict
import google.genai as genai
from google.genai import types
from dotenv import load_dotenv
import os

# Load the extracted entities
with open(
    'src/data/temp_data/article_entities.json', 'r', encoding='utf-8'
) as f:
    articles = json.load(f)


def get_unique_field_values(articles, field, is_list=False):
    unique_values = set()
    for article in articles:
        for entity in article.get('entities', []):
            if is_list:
                items = entity.get(field, [])
                for item in items:
                    if item:
                        unique_values.add(item)
            else:
                value = entity.get(field)
                if value:
                    unique_values.add(value)
    return unique_values


def prompt_gemini_for_unification(unique_items, prompt_text, output_file):
    item_list = sorted(list(unique_items))
    prompt = prompt_text + '\n' + '\n'.join(item_list)
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    client = genai.Client(api_key=api_key)
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                temperature=0.0,
            ),
            contents=prompt,
        )
        try:
            mapping = response.text
            if mapping.strip().startswith('{') or mapping.strip().startswith(
                '['
            ):
                import json as _json

                mapping = _json.loads(mapping)
        except Exception:
            mapping = response.text
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)
        print(f'Done. Saved unification mapping to {output_file}')
        return mapping
    except Exception as e:
        print(f'Gemini API error: {e}')
        return None


def canonicalize_actor(actor, actor_mapping):
    if not actor_mapping:
        return actor
    for canonical, variants in actor_mapping.items():
        if actor in variants:
            return canonical
    return actor


def canonicalize_location(location, location_mapping):
    if not location_mapping:
        return location
    for canonical, variants in location_mapping.items():
        if location in variants:
            return canonical
    return location


def canonicalize_articles(articles, actor_mapping, location_mapping):
    new_articles = []
    for article in articles:
        new_entities = []
        for entity in article.get('entities', []):
            # Canonicalize actors
            actors = entity.get('actors', [])
            new_actors = []
            for actor in actors:
                if isinstance(actor, str):
                    new_actors.append(canonicalize_actor(actor, actor_mapping))
                elif isinstance(actor, list):
                    new_actors.extend(
                        [
                            canonicalize_actor(a, actor_mapping)
                            for a in actor
                            if isinstance(a, str)
                        ]
                    )
            # Canonicalize location
            location = entity.get('location')
            if isinstance(location, str):
                new_location = canonicalize_location(
                    location, location_mapping
                )
            elif isinstance(location, list):
                # If location is a list, canonicalize each string
                new_location = [
                    canonicalize_location(loc, location_mapping)
                    for loc in location
                    if isinstance(loc, str)
                ]
            else:
                new_location = location
            # Copy entity and update
            new_entity = dict(entity)
            new_entity['actors'] = new_actors
            new_entity['location'] = new_location
            new_entities.append(new_entity)
        new_article = dict(article)
        new_article['entities'] = new_entities
        new_articles.append(new_article)
    return new_articles


def group_events_by_date(articles):
    grouped_by_date = defaultdict(list)
    per_date_events = defaultdict(list)
    for article in articles:
        for entity in article.get('entities', []):
            event_date = entity.get('event_date')
            if event_date:
                grouped_by_date[event_date].append(
                    {
                        'article_url': article['url'],
                        'title': article['title'],
                        'published_date': article['published_date'],
                        **entity,
                    }
                )
                per_date_events[event_date].append(
                    {
                        'event': entity.get('event'),
                        'details': entity.get('details'),
                        'actors': entity.get('actors'),
                        'location': entity.get('location'),
                        'article_url': article['url'],
                        'title': article['title'],
                        'published_date': article['published_date'],
                    }
                )
    return grouped_by_date, per_date_events


if __name__ == '__main__':
    # Call Gemini to unify actor names and save mapping
    print('Unifying actors...')
    unique_actors = get_unique_field_values(articles, 'actors', is_list=True)
    actor_prompt = (
        'Given the following list of actor names in Nepali, combine and reduce the set by merging different names that refer to the same actor. '
        "Return a key value pair such that the key is unified/canonical name, and the values are names that refer to the same actor, e.g.'Nepal Police' : 'Nepal Police', 'Nepal Police Force'"
    )
    prompt_gemini_for_unification(
        unique_actors, actor_prompt, 'src/data/actors.json'
    )

    print('Unifying locations...')
    unique_locations = get_unique_field_values(
        articles, 'location', is_list=True
    )
    location_prompt = (
        'Given the following list of location names in Nepali, combine and reduce the set by merging different names that refer to the same location. '
        "Return a key value pair such that the key is unified/canonical name, and the values are names that refer to the same actor, e.g.'पोखरा' : 'पोखरा', 'पोखरा, नेपाल'"
    )
    prompt_gemini_for_unification(
        unique_locations, location_prompt, 'src/data/locations.json'
    )

    print('Unifying article contents...')
    with open('src/data/actors.json', 'r', encoding='utf-8') as f:
        actor_mapping = json.load(f)
    with open('src/data/locations.json', 'r', encoding='utf-8') as f:
        location_mapping = json.load(f)
    articles_canonical = canonicalize_articles(
        articles, actor_mapping, location_mapping
    )

    # Group events by date using canonicalized articles, sort by date, and save only the final grouped events JSON
    grouped_by_date, per_date_events = group_events_by_date(articles_canonical)
    grouped_by_date_sorted = dict(sorted(grouped_by_date.items()))

    for date, events in grouped_by_date_sorted.items():
        for idx, event in enumerate(events, 1):
            event['id'] = f'{idx}'

    with open(
        'src/data/temp_data/grouped_events_by_date.json', 'w', encoding='utf-8'
    ) as f:
        json.dump(grouped_by_date_sorted, f, ensure_ascii=False, indent=2)
    print(
        'Saved grouped events by date to swrc/data/temp_data/grouped_events_by_date.json'
    )
