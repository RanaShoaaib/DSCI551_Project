import psycopg
from config import SCHEMA_FILE, SEED_FILE
from db import execute_sql_file, execute_query, execute_statement


def application_tables_exist(conn: psycopg.Connection) -> bool:
    """
    Check if required application tables exist.

    Args:
        conn: Active database connection.

    Returns:
        True if both users and items tables exist, otherwise False.
    """
    query = """
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name IN ('users', 'items');
    """
    _, rows = execute_query(conn, query)
    return rows is not None and rows[0][0] == 2


def initialize_database(conn : psycopg.Connection, force_initialize : bool = False) -> None:
    """
    Initialize database schema and seed data if not already present.

    Args:
        conn: Active database connection.
        force_initialize: If True, reinitialize even if tables exist.

    Returns:
        None.
    """
    if application_tables_exist(conn) and not force_initialize:
        print("Application tables already exist and force_initialize = False.")
        print("Skipping database initialization...")
        return
    print("Initializing application database...")
    execute_sql_file(conn, SCHEMA_FILE)
    execute_sql_file(conn, SEED_FILE)
    execute_statement(conn, "ANALYZE;")
    print("Database initialization complete.")
