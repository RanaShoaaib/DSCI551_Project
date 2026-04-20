from tabulate import tabulate

def get_menu_option() -> int:
    """
    Display main menu and return selected option.

    Args:
        None.

    Returns:
        Selected menu option as integer.
    """
    print("\nMain Menu:\n" + "="*10)
    print("1. Browse latest traffic items")
    print("2. Retrieve all crime items")
    print("3. Retrieve open items")
    print("4. Lookup items by user_id")
    print("5. Lookup items by user name")
    print("6. MVCC demonstration")
    print("7. Exit")

    while True:
        try:
            option = int(input("Select one of the above options by entering its index: "))
            if option in range(1, 8):
                return option
            print("Please enter a number between 1 and 7.")
        except ValueError:
            print("Invalid input. Please enter an integer between 1 and 7.")


def get_mode_option() -> str:
    """
    Display execution mode options and return selected mode.

    Args:
        None.

    Returns:
        Execution mode ('run', 'explain', or 'analyze').
    """
    modes_dict = {1: 'run', 2: 'explain', 3: 'analyze'}

    print("\nMode Menu:\n" + "=" * 10)
    print("1. Run query")
    print("2. Show EXPLAIN")
    print("3. Show EXPLAIN ANALYZE")
    while True:
        try:
            option = int(input("Select one of the above options by entering its index: "))
            if option in range(1, 4):
                return modes_dict[option]
            print("Please enter a number between 1 and 3.")
        except ValueError:
            print("Invalid input. Please enter an integer between 1 and 3.")


def print_query_output(header : list[str] | None, results : list[tuple] | None) -> None:
    """
    Print query results in tabular format.

    Args:
        header: Column names.
        results: Query result rows.

    Returns:
        None.
    """
    if not results:
        print("No rows returned.")
        return
    print(tabulate(results, headers=header, tablefmt="grid"))
    print()


def print_explain_output(header : list[str] | None, results : list[tuple] | None) -> None:
    """
    Print query execution plan output.

    Args:
        header: Plan header.
        results: Execution plan rows.

    Returns:
        None.
    """
    if not results:
        print("No plan returned.")
        return

    if header:
        print(header[0])
        print('=' * len(header[0]))

    for row in results:
        print(row[0])
    print()


def print_results(mode : str, header : list[str] | None, results : list[tuple] | None) -> None:
    """
    Print results based on execution mode.

    Args:
        mode: Execution mode.
        header: Column names or plan header.
        results: Query results or execution plan.

    Returns:
        None.
    """
    normalized_mode = mode.strip().lower()
    if normalized_mode == 'run':
        print_query_output(header,results)
    elif normalized_mode == 'explain' or normalized_mode == 'analyze':
        print_explain_output(header,results)
    else:
        raise ValueError(f"Invalid mode: {mode}")