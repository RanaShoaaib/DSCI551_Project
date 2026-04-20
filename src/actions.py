import psycopg
from db import execute_query, execute_explain, execute_explain_analyze

VALID_MODES = {'run','explain','analyze'}
VALID_CATEGORIES = {'traffic', 'crime', 'maintenance', 'miscellaneous'}
VALID_STATUS = {'open', 'closed'}


def get_sample_user_name(conn: psycopg.Connection) -> str:
    """
    Retrieve the user name with maximum number of associated items.

    Args:
        conn: Active database connection.

    Returns:
        User name string.
    """
    query = """
        SELECT u.name
        FROM users u JOIN items i ON i.user_id = u.id
        GROUP BY u.id, u.name
        ORDER BY COUNT(i.id) DESC, u.id
        LIMIT 1;
    """
    _, rows = execute_query(conn, query)
    if not rows:
        raise RuntimeError("No user found with associated items.")
    return rows[0][0]


def get_sample_user_id(conn: psycopg.Connection) -> int:
    """
    Retrieve the user ID with maximum number of associated items.

    Args:
        conn: Active database connection.

    Returns:
        User ID.
    """
    query = """
        SELECT u.id
        FROM users u JOIN items i ON i.user_id = u.id
        GROUP BY u.id
        ORDER BY COUNT(i.id) DESC, u.id
        LIMIT 1;
    """
    _, rows = execute_query(conn, query)
    if not rows:
        raise RuntimeError("No user found with associated items.")
    return rows[0][0]


def run_action(conn: psycopg.Connection, query: str, params: tuple | None = None, mode : str = 'run') -> tuple[list[str] | None, list[tuple] | None]:
    """
    Execute a query in run, explain, or analyze mode.

    Args:
        conn: Active database connection.
        query: SQL query to execute.
        params: Optional query parameters.
        mode: Execution mode ('run', 'explain', or 'analyze').

    Returns:
        Query results or execution plan.
    """
    if mode not in VALID_MODES:
        raise ValueError(f"Invalid mode: {mode}")
    match mode:
        case 'run':
            return execute_query(conn, query, params)
        case 'explain':
            return execute_explain(conn, query, params)
        case 'analyze':
            return execute_explain_analyze(conn, query, params)

def browse_recent_items(conn : psycopg.Connection, category : str, limit : int = 20, mode : str = 'run') -> tuple[list[str] | None, list[tuple] | None]:
    """
    Retrieve recent items for a category with ordering and limit.

    Args:
        conn: Active database connection.
        category: Item category filter.
        limit: Maximum number of rows to return.
        mode: Execution mode.

    Returns:
        Query results or execution plan.
    """
    category_normalized = category.strip().lower()
    if limit <= 0 or category_normalized not in VALID_CATEGORIES:
        raise ValueError("Invalid arguments")

    query = "SELECT * FROM items WHERE category = %s ORDER BY created_at DESC LIMIT %s;"
    params = (category_normalized, limit)
    return run_action(conn, query, params, mode)


def retrieve_items_by_category(conn : psycopg.Connection, category : str, mode : str = 'run') -> tuple[list[str] | None, list[tuple] | None]:
    """
    Retrieve all items for a given category.

    Args:
        conn: Active database connection.
        category: Item category filter.
        mode: Execution mode.

    Returns:
        Query results or execution plan.
    """
    category_normalized = category.strip().lower()
    if category_normalized not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category: {category}")

    query = "SELECT * FROM items WHERE category = %s ORDER BY created_at DESC;"
    params = (category_normalized,)
    return run_action(conn, query, params, mode)


def retrieve_items_by_status(conn : psycopg.Connection, status : str, mode : str = 'run') -> tuple[list[str] | None, list[tuple] | None]:
    """
    Retrieve items filtered by status.

    Args:
        conn: Active database connection.
        status: Item status filter.
        mode: Execution mode.

    Returns:
        Query results or execution plan.
    """
    status_normalized = status.strip().lower()
    if status_normalized not in VALID_STATUS:
        raise ValueError(f"Invalid status: {status}")

    query = "SELECT * FROM items WHERE status = %s;"
    params = (status_normalized,)
    return run_action(conn, query, params, mode)


def get_items_by_user_id(conn : psycopg.Connection, user_id : int, mode : str = 'run') -> tuple[list[str] | None, list[tuple] | None]:
    """
    Retrieve items for a specific user by ID.

    Args:
        conn: Active database connection.
        user_id: User identifier.
        mode: Execution mode.

    Returns:
        Query results or execution plan.
    """
    query = "SELECT * FROM users u JOIN items i ON i.user_id = u.id WHERE u.id = %s;"
    params = (user_id,)
    return run_action(conn, query, params, mode)

def get_items_by_user_name(conn : psycopg.Connection, user_name : str, mode : str = 'run') -> tuple[list[str] | None, list[tuple] | None]:
    """
    Retrieve items for a specific user by name.

    Args:
        conn: Active database connection.
        user_name: User name.
        mode: Execution mode.

    Returns:
        Query results or execution plan.
    """
    query = "SELECT * FROM users u JOIN items i ON i.user_id = u.id WHERE u.name = %s;"
    params = (user_name,)
    return run_action(conn, query, params, mode)