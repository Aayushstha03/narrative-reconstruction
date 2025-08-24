DROP TABLE IF EXISTS event_actors;
DROP TABLE IF EXISTS actor_aliases;
DROP TABLE IF EXISTS actors;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS sources;

CREATE TABLE actors (
    id SERIAL PRIMARY KEY,
    label TEXT NOT NULL
);

CREATE TABLE actor_aliases (
    id SERIAL PRIMARY KEY,
    actor_id INTEGER NOT NULL REFERENCES actors(id) ON DELETE CASCADE,
    alias TEXT NOT NULL
);

CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    published_date DATE NOT NULL
);

CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    label TEXT NOT NULL,
    details TEXT
);

CREATE TABLE event_actors (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    actor_id INTEGER NOT NULL REFERENCES actors(id) ON DELETE CASCADE
);

CREATE TABLE event_sources (
    id SERIAL PRIMARY KEY,
    event_id INT REFERENCES events(id) ON DELETE CASCADE,
    source_id INT REFERENCES sources(id) ON DELETE CASCADE
);
