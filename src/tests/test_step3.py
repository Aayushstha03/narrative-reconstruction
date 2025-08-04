import pytest
from src.step3_clean_extracted_events import (
    get_unique_field_values,
    canonicalize_actor,
    canonicalize_location,
    canonicalize_articles,
    group_events_by_date,
)


@pytest.mark.datatransform
def test_get_unique_field_values_list():
    articles = [
        {'entities': [{'actors': ['A', 'B'], 'location': 'X'}]},
        {'entities': [{'actors': ['B', 'C'], 'location': 'Y'}]},
    ]
    result = get_unique_field_values(articles, 'actors', is_list=True)
    assert result == {'A', 'B', 'C'}


@pytest.mark.datatransform
def test_get_unique_field_values_single():
    articles = [
        {'entities': [{'actors': ['A'], 'location': 'X'}]},
        {'entities': [{'actors': ['B'], 'location': 'Y'}]},
    ]
    result = get_unique_field_values(articles, 'location')
    assert result == {'X', 'Y'}


@pytest.mark.datatransform
def test_canonicalize_actor():
    mapping = {'Nepal Police': ['Nepal Police', 'Nepal Police Force']}
    assert canonicalize_actor('Nepal Police Force', mapping) == 'Nepal Police'
    assert canonicalize_actor('Random', mapping) == 'Random'


@pytest.mark.datatransform
def test_canonicalize_location():
    mapping = {'पोखरा': ['पोखरा', 'पोखरा, नेपाल']}
    assert canonicalize_location('पोखरा, नेपाल', mapping) == 'पोखरा'
    assert canonicalize_location('काठमाण्डौ', mapping) == 'काठमाण्डौ'


@pytest.mark.datatransform
def test_canonicalize_articles():
    articles = [
        {
            'entities': [
                {'actors': ['Nepal Police Force'], 'location': 'पोखरा, नेपाल'}
            ]
        }
    ]
    actor_mapping = {'Nepal Police': ['Nepal Police', 'Nepal Police Force']}
    location_mapping = {'पोखरा': ['पोखरा', 'पोखरा, नेपाल']}
    result = canonicalize_articles(articles, actor_mapping, location_mapping)
    assert result[0]['entities'][0]['actors'] == ['Nepal Police']
    assert result[0]['entities'][0]['location'] == 'पोखरा'


@pytest.mark.datatransform
def test_group_events_by_date():
    articles = [
        {
            'url': 'url1',
            'title': 'title1',
            'published_date': '2024-01-01',
            'entities': [
                {
                    'event_date': '2024-01-01',
                    'event': 'E1',
                    'details': 'D1',
                    'actors': ['A'],
                    'location': 'X',
                }
            ],
        },
        {
            'url': 'url2',
            'title': 'title2',
            'published_date': '2024-01-02',
            'entities': [
                {
                    'event_date': '2024-01-02',
                    'event': 'E2',
                    'details': 'D2',
                    'actors': ['B'],
                    'location': 'Y',
                }
            ],
        },
    ]
    grouped, per_date = group_events_by_date(articles)
    assert '2024-01-01' in grouped
    assert '2024-01-02' in grouped
    assert grouped['2024-01-01'][0]['event'] == 'E1'
    assert per_date['2024-01-02'][0]['event'] == 'E2'
