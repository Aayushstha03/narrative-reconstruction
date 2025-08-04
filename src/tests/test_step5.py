import os
import pytest


# Test DB connection string from environment
def test_db_connection():
    import psycopg

    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    conn_str = f'dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}'
    try:
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT 1;')
                assert cur.fetchone()[0] == 1
    except Exception as e:
        pytest.fail(f'Database connection failed: {e}')
