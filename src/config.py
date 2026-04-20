import os
from pathlib import Path
from dotenv import load_dotenv

SCHEMA_FILE = Path(__file__).parent.parent / "sql/schema.sql"
SEED_FILE = Path(__file__).parent.parent / "sql/seed.sql"
MVCC_SETUP_FILE = Path(__file__).parent.parent / "sql/mvcc.sql"


def validate_db_config(db_config: dict[str, str | int]) -> None:
    """
    Validate required database configuration values.

    Args:
        db_config: Dictionary containing database connection parameters.

    Returns:
        None.
    """
    for k,v in db_config.items():
        if not v:
            raise ValueError(f"Empty required config: {k}")

    try:
        int(db_config["port"])
    except ValueError:
        raise ValueError("Port must be a valid integer")


def load_db_config() -> dict[str, str | int]:
    """
    Load and validate database configuration from environment variables.

    Args:
        None.

    Returns:
        Dictionary containing validated database configuration.
    """
    load_dotenv()
    db_config = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "dbname": os.getenv("DB_NAME"),
    }

    validate_db_config(db_config)
    db_config["port"] = int(db_config["port"])
    return db_config