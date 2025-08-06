import pytest
from src.insert_into_db import process_article, connect_db, load_env


@pytest.fixture(scope='function')
def db():
    """Set up and tear down temp tables."""
    config = load_env()
    conn = connect_db(config)
    cur = conn.cursor()

    cur.execute("""
    CREATE TEMP TABLE sources (
        source_id SERIAL PRIMARY KEY,
        source_url TEXT UNIQUE NOT NULL
    );
    """)

    cur.execute("""
    CREATE TEMP TABLE entities (
        entity_id SERIAL PRIMARY KEY,
        entity_name TEXT NOT NULL,
        type TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TEMP TABLE triples (
        triple_id SERIAL PRIMARY KEY,
        subject_id INTEGER NOT NULL,
        predicate TEXT NOT NULL,
        object_id INTEGER NOT NULL,
        date DATE,
        details TEXT,
        source_id INTEGER NOT NULL
    );
    """)

    conn.commit()
    yield conn
    conn.close()


valid_article = {
    'url': 'https://example.com',
    'title': 'Test',
    'published_date': '2025-01-01',
    'entities': [
        {
            'subject': {'name': 'Alice', '@type': 'Person'},
            'predicate': 'organized',
            'object': {'name': 'Tech Conference', '@type': 'Event'},
            '_date': '2025-08-01',
            'details': 'Annual event.',
        }
    ],
}

broken_article = {
    'url': 'https://example.com',
    'title': 'Test',
    'published_date': '2025-01-01',
    'entities': [
        {
            'subject': {'name': 'Alice', '@type': None},
            'predicate': 'organized',
            'object': {'@type': 'Event', 'name': 'Tech Conference'},
            '_date': '2025-08-01',
            'details': 'Should fail.',
        }
    ],
}


def test_successful_insert(db):
    process_article(db, valid_article)
    db.commit()
    cur = db.cursor()
    cur.execute('SELECT COUNT(*) FROM triples')
    assert cur.fetchone()[0] == 1


def test_transaction_atomicity(db):
    """Ensure a failing triple insertion doesn't leave orphaned records."""

    process_article(db, broken_article)
    db.commit()

    cur = db.cursor()

    for table in ['triples', 'sources', 'entities']:
        cur.execute(f'SELECT COUNT(*) FROM {table}')
        assert cur.fetchone()[0] == 0
