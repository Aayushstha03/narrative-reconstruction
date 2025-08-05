import json
import os
from dotenv import load_dotenv
import psycopg


def load_env():
    load_dotenv()
    return {
        "dbname": os.getenv("POSTGRES_DB"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", 5432))
    }


def connect_db(config):
    print(config)
    conn = psycopg.connect(
        dbname=config["dbname"],
        user=config["user"],
        password=config["password"],
        host=config["host"],
        port=config["port"]
    )
    conn.autocommit = True
    return conn, conn.cursor()


def load_json(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def insert_source(cur, url: str):
    cur.execute(
        "INSERT INTO sources (source_url) VALUES (%s) RETURNING source_id",
        (url,)
    )
    return cur.fetchone()[0]


def get_or_create_entity(cur, name: str, _type: str):
    cur.execute(
        "SELECT entity_id FROM entities WHERE entity_name = %s AND type = %s",
        (name, _type)
    )
    row = cur.fetchone()
    if row:
        return row[0]
    else:
        cur.execute(
            "INSERT INTO entities (entity_name, type) VALUES (%s, %s) RETURNING entity_id",
            (name, _type)
        )
        return cur.fetchone()[0]


def process_triples(cur, triples_data: list, source_id: int):
    for triple in triples_data:
        subject = triple["subject"]
        _object = triple["object"]

        subject_id = get_or_create_entity(cur, subject["name"], subject["@type"])

        if "name" in _object:
            object_name = _object["name"]
        elif "value" in _object:
            object_name = str(_object["value"])
    
    
        object_id = get_or_create_entity(cur, object_name, _object["@type"])

        predicate = triple["predicate"]
        details = triple.get("details")
        _date = triple.get("_date")

        cur.execute(
            """
            INSERT INTO triples (
                subject_id, predicate, object_id, date, details, source_id
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (subject_id, predicate, object_id, _date, details, source_id)
        )


def main():
    config = load_env()
    conn, cur = connect_db(config)

    articles = load_json("src/data/article_triples.json")

    for article in articles:
        source_url = article["url"]
        source_id = insert_source(cur, source_url)
        process_triples(cur, article["entities"], source_id)

    print("Data inserted successfully.")
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
