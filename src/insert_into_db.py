import json
import os
import psycopg


def load_env():
    return {
        'dbname': os.getenv('POSTGRES_DB'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD'),
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRES_PORT', 5432)),
    }


def connect_db(config):
    try:
        return psycopg.connect(**config)
    except psycopg.Error as e:
        print(f'Database connection failed: {e}')
        raise


def load_json(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_or_create_source(cur, source_url: str):
    """Retrieve the source ID for a given URL, or insert it if it doesn't exist."""
    try:
        cur.execute(
            'SELECT source_id FROM sources WHERE source_url = %s;',
            (source_url,),
        )
        result = cur.fetchone()
        if result:
            return result[0]

        cur.execute(
            'INSERT INTO sources (source_url) VALUES (%s) RETURNING source_id;',
            (source_url,),
        )
        return cur.fetchone()[0]
    except psycopg.Error as e:
        print(f'Error getting or inserting source: {e}')
        raise


def get_or_create_entity(cur, name: str, _type: str):
    """Retrieve the entity ID for a given name and type, or insert it if it doesn't exist."""
    try:
        cur.execute(
            'SELECT entity_id FROM entities WHERE entity_name = %s AND type = %s;',
            (name, _type),
        )
        row = cur.fetchone()
        if row:
            return row[0]

        cur.execute(
            'INSERT INTO entities (entity_name, type) VALUES (%s, %s) RETURNING entity_id;',
            (name, _type),
        )
        return cur.fetchone()[0]
    except psycopg.Error as e:
        print(f'Database error in get_or_create_entity: {e}')
        raise


def process_article(conn, article: dict):
    """Process a single article and insert its triples into the database."""

    for triple in article['entities']:
        with conn.transaction():
            with conn.cursor() as cur:
                try:
                    source_id = get_or_create_source(cur, article['url'])

                    subject = triple['subject']
                    _object = triple['object']

                    subject_id = get_or_create_entity(
                        cur, subject['name'], subject['@type']
                    )

                    if 'name' in _object:
                        object_name = _object['name']
                    elif 'value' in _object:
                        object_name = str(_object['value'])

                    object_id = get_or_create_entity(
                        cur, object_name, _object['@type']
                    )

                    predicate = triple['predicate']
                    details = triple.get('details')
                    _date = triple.get('_date')

                    cur.execute(
                        """
                        INSERT INTO triples (
                            subject_id, predicate, object_id, date, details, source_id
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (
                            subject_id,
                            predicate,
                            object_id,
                            _date,
                            details,
                            source_id,
                        ),
                    )
                except (psycopg.Error, ValueError) as e:
                    print(f'Error inserting triple: {triple}')
                    print(e)


def main():
    config = load_env()
    conn = connect_db(config)

    articles = load_json('src/data/article_triples.json')

    for article in articles:
        process_article(conn, article)

    print('Data inserted successfully.')
    conn.close()


if __name__ == '__main__':
    main()
