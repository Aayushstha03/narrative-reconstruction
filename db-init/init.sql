-- Create table for entities
CREATE TABLE entities (
    entity_id SERIAL PRIMARY KEY,
    entity_name TEXT NOT NULL,
    type TEXT NOT NULL
);

-- Create table for sources
CREATE TABLE sources (
    source_id SERIAL PRIMARY KEY,
    source_url TEXT NOT NULL
);

-- Create table for triples
CREATE TABLE triples (
    triple_id SERIAL PRIMARY KEY,
    subject_id INT NOT NULL,
    predicate TEXT NOT NULL,
    object_id INT NOT NULL,
    date DATE,
    details TEXT,
    source_id INT,
    FOREIGN KEY (subject_id) REFERENCES entities(entity_id) ON DELETE CASCADE,
    FOREIGN KEY (object_id) REFERENCES entities(entity_id) ON DELETE CASCADE,
    FOREIGN KEY (source_id) REFERENCES sources(source_id) ON DELETE SET NULL
);
