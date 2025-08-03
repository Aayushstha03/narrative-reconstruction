import psycopg
import os

import networkx as nx


DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

conn = psycopg.connect(
    f'dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}'
)

date_from = '2025-01-01'

G = nx.DiGraph()

with conn.cursor() as cur:
    cur.execute(
        """
        SELECT
            a.id AS actor_id, a.label AS actor_label,
            e.id AS event_id, e.label AS event_label, e.details AS event_details,
            s.id AS source_id, s.title AS source_title, s.url AS source_url, s.published_date
        FROM sources s
        JOIN event_sources es ON s.id = es.source_id
        JOIN events e ON es.event_id = e.id
        JOIN event_actors ea ON e.id = ea.event_id
        JOIN actors a ON ea.actor_id = a.id
        WHERE s.published_date >= %s
    """,
        (date_from,),
    )

    rows = cur.fetchall()


actor_nodes = {}
event_nodes = {}
source_nodes = {}

for row in rows:
    (
        actor_id,
        actor_label,
        event_id,
        event_label,
        event_details,
        source_id,
        source_title,
        source_url,
        published_date,
    ) = row

    if actor_id not in actor_nodes:
        G.add_node(f'actor_{actor_id}', label=actor_label, role='actor')
        actor_nodes[actor_id] = True

    if event_id not in event_nodes:
        G.add_node(
            f'event_{event_id}',
            label=event_label,
            details=event_details,
            role='event',
        )
        event_nodes[event_id] = True

    if source_id not in source_nodes:
        G.add_node(
            f'source_{source_id}',
            label=source_title,
            url=source_url,
            published_date=str(published_date),
            role='source',
        )
        source_nodes[source_id] = True

    # Add edges
    G.add_edge(f'actor_{actor_id}', f'event_{event_id}')
    G.add_edge(f'event_{event_id}', f'source_{source_id}')
    # G.add_edge(f"actor_{actor_id}", f"source_{source_id}")

nx.write_gexf(G, 'src/knowledge_graph.gexf')
print('GEXF saved as knowledge_graph.gexf')
