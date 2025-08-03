import psycopg
import os
import json

# Load DB connection from env
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')


conn_str = f'dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}'


with open('src/data/actors.json', 'r', encoding='utf-8') as f:
    actors_data = json.load(f)


with open('src/data/reconstructed_narrative.json', 'r', encoding='utf-8') as f:
    narrative_data = json.load(f)


def insert_actors():
    """Insert actors and their aliases into the database."""
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM actor_aliases;')
            cur.execute('DELETE FROM actors;')

            for label, aliases in actors_data.items():
                # Insert actor
                cur.execute(
                    'INSERT INTO actors (label) VALUES (%s) RETURNING id;',
                    (label,),
                )
                actor_id = cur.fetchone()[0]

                # Insert aliases
                for alias in aliases:
                    if alias != label:
                        cur.execute(
                            'INSERT INTO actor_aliases (actor_id, alias) VALUES (%s, %s);',
                            (actor_id, alias),
                        )

            conn.commit()

            # Check data
            cur.execute('SELECT * FROM actors LIMIT 3;')
            print('Actors:')
            for row in cur.fetchall():
                print(row)

            cur.execute('SELECT * FROM actor_aliases LIMIT 3;')
            print('\nActor Aliases:')
            for row in cur.fetchall():
                print(row)


def insert_narrative():
    """Insert events, sources, and cross-references into the database."""
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM event_actors;')
            cur.execute('DELETE FROM event_sources;')
            cur.execute('DELETE FROM events;')
            cur.execute('DELETE FROM sources;')

            for date_key, events in narrative_data.items():
                for event in events:
                    # Insert event first
                    event_label = event['event']
                    details = event['details']

                    cur.execute(
                        """
                        INSERT INTO events (label, details)
                        VALUES (%s, %s)
                        RETURNING id;
                        """,
                        (event_label, details),
                    )
                    event_id = cur.fetchone()[0]

                    # For each source in this event
                    for source in event['sources']:
                        source_url = source['article_url']
                        # Check if source exists
                        cur.execute(
                            'SELECT id FROM sources WHERE url = %s;',
                            (source_url,),
                        )
                        source_id = cur.fetchone()
                        if source_id:
                            source_id = source_id[0]
                        else:
                            title = source['title']
                            published_date = source['published_date'].split(
                                ' '
                            )[0]
                            cur.execute(
                                'INSERT INTO sources (title, url, published_date) VALUES (%s, %s, %s) RETURNING id;',
                                (title, source_url, published_date),
                            )
                            source_id = cur.fetchone()[0]

                        # Link event with source
                        cur.execute(
                            'INSERT INTO event_sources (event_id, source_id) VALUES (%s, %s);',
                            (event_id, source_id),
                        )

                    # For each actor in this event
                    for actor_label in event['actors']:
                        cur.execute(
                            'SELECT id FROM actors WHERE label = %s;',
                            (actor_label,),
                        )
                        result = cur.fetchone()

                        if result:
                            actor_id = result[0]
                        else:
                            cur.execute(
                                'INSERT INTO actors (label) VALUES (%s) RETURNING id;',
                                (actor_label,),
                            )
                            actor_id = cur.fetchone()[0]

                        cur.execute(
                            'INSERT INTO event_actors (event_id, actor_id) VALUES (%s, %s);',
                            (event_id, actor_id),
                        )

            conn.commit()

            cur.execute('SELECT * FROM events LIMIT 3;')
            print('\nEvents:')
            for row in cur.fetchall():
                print(row)

            cur.execute('SELECT * FROM event_sources LIMIT 3;')
            print('\nEvent-Sources:')
            for row in cur.fetchall():
                print(row)

            cur.execute('SELECT * FROM event_actors LIMIT 3;')
            print('\nEvent-Actors:')
            for row in cur.fetchall():
                print(row)


if __name__ == '__main__':
    insert_actors()
    insert_narrative()
