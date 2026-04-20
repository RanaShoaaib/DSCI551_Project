import psycopg
from pathlib import Path
from config import load_db_config


def get_connection() -> psycopg.Connection:
    """
    Establish a connection to the PostgreSQL database.

    Args:
        None.

    Returns:
        psycopg.Connection object.
    """
    db_config = load_db_config()
    try:
        conn = psycopg.connect(**db_config)
    except Exception as e:
        raise RuntimeError(f"Database connection failed: {e}")
    return conn


def execute_query(conn : psycopg.Connection, query : str, params : tuple | None = None) -> tuple[list[str] | None, list[tuple] | None]:
    """
    Execute a SQL query and return results if available.

    Args:
        conn: Active database connection.
        query: SQL query to execute.
        params: Optional query parameters.

    Returns:
        Tuple of column names and result rows, or (None, None) for non-select queries.
    """
    with conn.cursor() as cursor:
        if params is not None:
            cursor.execute(query, params)
        else :
            cursor.execute(query)

        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return columns, rows
        else:
            return None, None


def execute_explain(conn : psycopg.Connection, query : str, params : tuple | None = None) -> tuple[list[str] | None, list[tuple] | None]:
    """
    Execute EXPLAIN on a SQL query.

    Args:
        conn: Active database connection.
        query: SQL query to analyze.
        params: Optional query parameters.

    Returns:
        Query execution plan.
    """
    explain_query = f"EXPLAIN {query}"
    return execute_query(conn, explain_query, params)


def execute_explain_analyze(conn : psycopg.Connection, query : str, params : tuple | None = None) -> tuple[list[str] | None, list[tuple] | None]:
    """
    Execute EXPLAIN ANALYZE with buffer statistics on a SQL query.

    Args:
        conn: Active database connection.
        query: SQL query to analyze.
        params: Optional query parameters.

    Returns:
        Execution plan with runtime and buffer details.
    """
    explain_analyze_query = f"EXPLAIN (ANALYZE,BUFFERS) {query}"
    try:
        execute_query(conn, "BEGIN;")
        columns, plan = execute_query(conn, explain_analyze_query, params)
        return columns, plan
    finally:
        conn.rollback()


def execute_statement(conn : psycopg.Connection, query : str, params : tuple | None = None) -> None:
    """
    Execute a SQL statement and commit the transaction.

    Args:
        conn: Active database connection.
        query: SQL statement to execute.
        params: Optional query parameters.

    Returns:
        None.
    """
    with conn.cursor() as cursor:
        if params is not None:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
    conn.commit()


def execute_sql_file(conn : psycopg.Connection, file : Path) -> None:
    """
    Execute multiple SQL statements from a file.

    Args:
        conn: Active database connection.
        file: Path to SQL file.

    Returns:
        None.
    """
    with open(file, "r") as f:
        queries = [q.strip() + ';' for q in f.read().split(';') if q.strip()]
    with conn.cursor() as cursor:
        for query in queries:
            cursor.execute(query)
    conn.commit()