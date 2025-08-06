import json
import builtins
from src.extract_triples import main

# Mock data
mock_article = {
    'url': 'https://example.com/news/123',
    'title': 'Sample News Title',
    'published_date': '2024-01-01',
    'content': 'This is sample content',
}

mock_response = [
    {
        'subject': {
            '@type': 'Person',
            'name': 'Sample Name',
            'id': 'person:sample-person',
            'additionalProperties': {},
        },
        'predicate': 'organizer',
        'object': {
            '@type': 'Event',
            'name': 'Sample Event',
            'id': 'event:sample-event',
            'additionalProperties': {},
        },
        'time_expression': '2025-01-01',
        '_date': '2025-01-01',
        'time': '13:00:00',
        'details': 'Sample event details.',
    }
]

expected_output = [
    {
        'url': mock_article['url'],
        'title': mock_article['title'],
        'published_date': mock_article['published_date'],
        'entities': mock_response,
    }
]


def test_triples_extraction(monkeypatch):
    article_path = 'tests/data/article_contents.json'
    triples_path = 'tests/data/article_triples.json'

    # Write mock article content to the expected path
    with open(article_path, 'w', encoding='utf-8') as f:
        json.dump([mock_article], f)

    # Monkeypatch Gemini LLM function
    def mock_call_gemini_llm(article, prompt):
        return {'entities': mock_response}

    monkeypatch.setattr(
        'src.extract_triples.call_gemini_llm', mock_call_gemini_llm
    )

    # Monkeypatch open() for specific paths to use test files
    real_open = builtins.open

    def patched_open(file, *args, **kwargs):
        if file == 'src/data/article_contents.json':
            file = article_path
        elif file == 'src/data/article_triples.json':
            file = triples_path
        return real_open(file, *args, **kwargs)

    monkeypatch.setattr('builtins.open', patched_open)

    # Run the script
    main()

    # Load and verify output
    with open(triples_path, encoding='utf-8') as f:
        data = json.load(f)

    assert data == expected_output
