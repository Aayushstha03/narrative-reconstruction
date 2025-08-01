DROP TABLE IF EXISTS actor_aliases;
DROP TABLE IF EXISTS actors;


CREATE TABLE actors (
    id SERIAL PRIMARY KEY,
    label TEXT NOT NULL
);


CREATE TABLE actor_aliases (
    id SERIAL PRIMARY KEY,
    actor_id INTEGER NOT NULL REFERENCES actors(id) ON DELETE CASCADE,
    alias TEXT NOT NULL
);

