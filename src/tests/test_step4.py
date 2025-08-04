import json
import tempfile
import os
from src.step4_create_narrative import (
    extract_event_fields_by_date,
    enrich_narrative_with_source_articles,
)


def test_extract_event_fields_by_date():
    sample = {
        '2024-01-01': [
            {
                'id': '1',
                'event': 'E1',
                'details': 'D1',
                'actors': ['A'],
                'extra': 'ignore',
            },
            {
                'id': '2',
                'event': 'E2',
                'details': 'D2',
                'actors': ['B'],
                'extra': 'ignore',
            },
        ]
    }
    with tempfile.NamedTemporaryFile(
        mode='w+', encoding='utf-8', delete=False
    ) as f:
        json.dump(sample, f)
        f.flush()
        result = extract_event_fields_by_date(f.name)
    assert '2024-01-01' in result
    assert result['2024-01-01'][0]['event'] == 'E1'
    assert 'extra' not in result['2024-01-01'][0]
    os.remove(f.name)


def test_enrich_narrative_with_source_articles():
    grouped_events = {
        '2024-01-01': [
            {
                'id': '1',
                'title': 'T1',
                'article_url': 'U1',
                'published_date': '2024-01-01',
                'event': 'E1',
                'details': 'D1',
                'actors': ['A'],
            },
            {
                'id': '2',
                'title': 'T2',
                'article_url': 'U2',
                'published_date': '2024-01-01',
                'event': 'E2',
                'details': 'D2',
                'actors': ['B'],
            },
        ]
    }
    narrative = {
        '2024-01-01': [
            {
                'event': 'E1',
                'details': 'D1',
                'actors': ['A'],
                'source_event_indices': ['1'],
            },
            {
                'event': 'E2',
                'details': 'D2',
                'actors': ['B'],
                'source_event_indices': ['2'],
            },
        ]
    }
    with (
        tempfile.NamedTemporaryFile(
            mode='w+', encoding='utf-8', delete=False
        ) as f1,
        tempfile.NamedTemporaryFile(
            mode='w+', encoding='utf-8', delete=False
        ) as f2,
    ):
        json.dump(grouped_events, f1)
        f1.flush()
        json.dump(narrative, f2)
        f2.flush()
        enrich_narrative_with_source_articles(f1.name, f2.name)
        with open(f2.name, 'r', encoding='utf-8') as f:
            enriched = json.load(f)
    assert 'sources' in enriched['2024-01-01'][0]
    assert enriched['2024-01-01'][0]['sources'][0]['title'] == 'T1'
    assert 'source_event_indices' not in enriched['2024-01-01'][0]
    os.remove(f1.name)
    os.remove(f2.name)
