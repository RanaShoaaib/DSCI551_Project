import psycopg
from psycopg import sql
from config import MVCC_SETUP_FILE
from db import get_connection, execute_sql_file, execute_query, execute_statement
from utils import print_query_output


def get_mvcc_option() -> int:
    """
    Display MVCC menu and return selected option.

    Args:
        None.

    Returns:
        Selected menu option as integer.
    """
    print("\nMVCC Menu:\n" + "=" * 10)
    print("1. Demonstrate tuple versioning and VACUUM")
    print("2. Demonstrate READ COMMITTED isolation")
    print("3. Demonstrate REPEATABLE READ isolation")
    print("4. Back to main menu")

    while True:
        try:
            option = int(input("Select one of the above options by entering its index: "))
            if option in range(1, 5):
                return option
            print("Please enter a number between 1 and 4.")
        except ValueError:
            print("Invalid input. Please enter an integer between 1 and 4.")


def show_state_with_ctid(conn : psycopg.Connection, table_name : str) -> None:
    """
    Display table rows with tuple IDs and tuple statistics.

    Args:
        conn: Active database connection.
        table_name: Table name.

    Returns:
        None.
    """
    query = sql.SQL("SELECT ctid, * FROM {} ORDER BY id").format(sql.Identifier(table_name))
    with conn.cursor() as cursor:
        cursor.execute(query)
        header = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        print_query_output(header, results)


def show_pgstattuple_stats(conn: psycopg.Connection, table_name: str) -> None:
    """
    Display exact tuple statistics using pgstattuple.

    Args:
        conn: Active database connection.
        table_name: Table name.

    Returns:
        None.
    """
    query = "SELECT tuple_count, dead_tuple_count, dead_tuple_len FROM pgstattuple(%s);"
    header, results = execute_query(conn, query, (table_name,))
    print("pgstattuple statistics:")
    print_query_output(header, results)


def run_vacuum(conn: psycopg.Connection, table_name: str) -> None:
    """
    Execute VACUUM on a table.

    Args:
        conn: Active database connection.
        table_name: Table name.

    Returns:
        None.
    """
    vacuum_query = sql.SQL("VACUUM {}").format(sql.Identifier(table_name))
    old_autocommit = conn.autocommit
    try:
        conn.commit()
        conn.autocommit = True
        with conn.cursor() as cursor:
            cursor.execute(vacuum_query)
    finally:
        conn.autocommit = old_autocommit


def execute_statement_no_commit(conn : psycopg.Connection, query : str, params : tuple | None = None) -> None:
    """
    Execute a SQL statement without committing.

    Args:
        conn: Active database connection.
        query: SQL statement.
        params: Optional query parameters.

    Returns:
        None.
    """
    with conn.cursor() as cursor:
        if params is None:
            cursor.execute(query)
        else:
            cursor.execute(query, params)


def format_query(query: str, params: tuple | None) -> str:
    """
    Format a query string with parameters for display.

    Args:
        query: SQL query.
        params: Query parameters.

    Returns:
        Formatted query string.
    """
    if not params:
        return query
    for param in params:
        if isinstance(param, str):
            param = f"'{param}'"
        query = query.replace("%s", str(param), 1)
    return query


def show_session_state(session_id : str, conn : psycopg.Connection, query : str, params: tuple | None = None) -> None:
    """
    Display query and result for a session.

    Args:
        session_id: Identifier for the session.
        conn: Active database connection.
        query: SQL query.
        params: Optional query parameters.

    Returns:
        None.
    """
    title = f"Connection {session_id}"
    print(title)
    print("-" * len(title))

    formatted_query = format_query(query, params)
    print(f"Query: {formatted_query}")

    header, result = execute_query(conn, query, params)
    print("Output:")
    print_query_output(header, result)


def demo_vacuum(conn : psycopg.Connection) -> None:
    """
    Demonstrate tuple versioning and VACUUM behavior.

    Args:
        conn: Active database connection.

    Returns:
        None.
    """
    iphone_price_update = "UPDATE phones SET price = price + 10 WHERE name = 'iphone 16';"

    execute_statement(conn, "CREATE EXTENSION IF NOT EXISTS pgstattuple;")

    print("\nOriginal State\n" + "=" * 14)
    print("Table:")
    show_state_with_ctid(conn, "phones")
    show_pgstattuple_stats(conn, "phones")

    num = 100
    print(f"Updating price of iphone 16 to increase by 10, {num} times")
    for _ in range(num):
        execute_statement(conn, iphone_price_update)

    print("\nBefore Vacuum\n" + "=" * 13)
    print("Table:")
    show_state_with_ctid(conn, "phones")
    show_pgstattuple_stats(conn, "phones")

    print("\nAfter Vacuum\n" + "="*12)
    run_vacuum(conn, "phones")
    print("Table:")
    show_state_with_ctid(conn, "phones")
    show_pgstattuple_stats(conn, "phones")


def demo_reads(conn_a: psycopg.Connection, conn_b: psycopg.Connection, mode: str) -> None:
    """
    Demonstrate MVCC behavior under different isolation levels.

    Args:
        conn_a: First database connection.
        conn_b: Second database connection.
        mode: Isolation mode ('committed' or 'repeatable').

    Returns:
        None.
    """
    mode_normalized = mode.strip().lower()
    if mode_normalized not in {"committed", "repeatable"}:
        raise ValueError(f"Invalid mode: {mode}")

    results_query = "SELECT * FROM phones WHERE name = %s;"
    update_query = "UPDATE phones SET price = price - 100 WHERE name = %s;"
    name = "pixel 10"

    try:
        execute_statement_no_commit(conn_a, "BEGIN;")
        if mode_normalized == "committed":
            execute_statement_no_commit(conn_b, "BEGIN;")
        else:
            execute_statement_no_commit(conn_b, "BEGIN ISOLATION LEVEL REPEATABLE READ;")

        print("\nInitial State\n" + "=" * 13)
        show_session_state("A", conn_a, results_query, (name,))
        show_session_state("B", conn_b, results_query, (name,))

        execute_statement_no_commit(conn_a, update_query, (name,))
        print("\nState after Connection A decreases price by 100 but does not commit\n" + "=" * 67)
        show_session_state("A", conn_a, results_query, (name,))
        show_session_state("B", conn_b, results_query, (name,))

        conn_a.commit()
        print("\nState after Connection A commits\n" + "=" * 32)
        show_session_state("A", conn_a, results_query, (name,))
        show_session_state("B", conn_b, results_query, (name,))
    finally:
        conn_a.rollback()
        conn_b.rollback()


def demo_mvcc():
    """
    Run interactive MVCC demonstrations.

    Args:
        None.

    Returns:
        None.
    """
    with get_connection() as conn_a, get_connection() as conn_b:
        while True:
            option = get_mvcc_option()
            if option == 4:
                break
            match option:
                case 1:
                    execute_sql_file(conn_a, MVCC_SETUP_FILE)
                    demo_vacuum(conn_a)
                case 2:
                    execute_sql_file(conn_a, MVCC_SETUP_FILE)
                    demo_reads(conn_a, conn_b, "committed")
                case 3:
                    execute_sql_file(conn_a, MVCC_SETUP_FILE)
                    demo_reads(conn_a, conn_b, "repeatable")
