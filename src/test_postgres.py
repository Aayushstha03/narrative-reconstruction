import psycopg
import os

# Load DB connection parameters from environment variables, with defaults
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Sample data to insert
sample_data = [(1, "Alice"), (2, "Bob"), (3, "Charlie")]


def main():
    # Connect to PostgreSQL using context manager (psycopg 3 style)
    conn_str = f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}"
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            # Create test table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS test_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                );
            """)
            # Insert sample data
            cur.execute("DELETE FROM test_table;")
            cur.executemany(
                "INSERT INTO test_table (id, name) VALUES (%s, %s);", sample_data
            )
            # Query and print data
            cur.execute("SELECT * FROM test_table;")
            rows = cur.fetchall()
            print("Rows in test_table:")
            for row in rows:
                print(row)


if __name__ == "__main__":
    main()
