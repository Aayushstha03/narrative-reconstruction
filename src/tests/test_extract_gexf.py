import networkx as nx
from .. import extract_gexf


def test_fetch_joined_tuples(monkeypatch):
    """
    Test fetch_joined_tuples by monkeypatching psycopg.connect
    to return fake joined rows.
    """

    # Fake DB rows
    fake_rows = [
        (
            1,
            'Actor A',
            2,
            'Event B',
            'Some details',
            3,
            'Source X',
            'http://example.com',
            '2025-07-31',
        )
    ]

    # Fake connection and cursor
    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

        def execute(self, *a, **kw):
            pass

        def fetchall(self):
            return fake_rows

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

    # Patch psycopg.connect
    monkeypatch.setattr(
        extract_gexf.psycopg, 'connect', lambda *a, **kw: FakeConnection()
    )

    rows = extract_gexf.fetch_joined_tuples('2025-01-01')
    assert rows == fake_rows
    assert isinstance(rows, list)
    assert len(rows) == 1


def test_build_graph_creates_expected_graph():
    """
    Test build_graph with a fake row.
    """

    fake_rows = [
        (
            1,
            'Actor A',
            2,
            'Event B',
            'Some details',
            3,
            'Source X',
            'http://example.com',
            '2025-07-31',
        )
    ]

    G = extract_gexf.build_graph(fake_rows)

    assert isinstance(G, nx.DiGraph)

    # Expect exactly 3 nodes: actor, event, source
    assert G.number_of_nodes() == 3

    roles = nx.get_node_attributes(G, 'role').values()
    assert 'actor' in roles
    assert 'event' in roles
    assert 'source' in roles

    # Edges: actor -> event -> source
    assert G.has_edge('actor_1', 'event_2')
    assert G.has_edge('event_2', 'source_3')

    # Node attributes
    actor_node = G.nodes['actor_1']
    assert actor_node['label'] == 'Actor A'
    assert actor_node['role'] == 'actor'

    event_node = G.nodes['event_2']
    assert event_node['label'] == 'Event B'
    assert event_node['details'] == 'Some details'
    assert event_node['role'] == 'event'

    source_node = G.nodes['source_3']
    assert source_node['label'] == 'Source X'
    assert source_node['url'] == 'http://example.com'
    assert source_node['published_date'] == '2025-07-31'
    assert source_node['role'] == 'source'
