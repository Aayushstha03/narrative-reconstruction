import psycopg
import os
import json

# Load DB connection from env
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")



with open("src/data.json", "r", encoding="utf-8") as f:
    actors_data = json.load(f)

def insert_actors():
    conn_str = f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}"

    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
          
            cur.execute("DELETE FROM actor_aliases;")
            cur.execute("DELETE FROM actors;")

            for label, aliases in actors_data.items():
                # Insert actor
                cur.execute(
                    "INSERT INTO actors (label) VALUES (%s) RETURNING id;",
                    (label,)
                )
                actor_id = cur.fetchone()[0]

                # If multiple aliases, insert the extras
                if len(aliases) > 1:
                    for alias in aliases:
                        if alias != label:
                            cur.execute(
                                "INSERT INTO actor_aliases (actor_id, alias) VALUES (%s, %s);",
                                (actor_id, alias)
                            )
           
            conn.commit()

            # Check data
            cur.execute("SELECT * FROM actors;")
            print("Actors:")
            for row in cur.fetchall():
                print(row)

            cur.execute("SELECT * FROM actor_aliases;")
            print("\nActor Aliases:")
            for row in cur.fetchall():
                print(row)


if __name__ == "__main__":
    insert_actors()
