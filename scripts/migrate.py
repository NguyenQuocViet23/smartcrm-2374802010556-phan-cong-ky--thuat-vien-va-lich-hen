"""Apply SQL migrations from db/migrations in filename order."""

from pathlib import Path
import os

import psycopg
from dotenv import load_dotenv

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS_DIRECTORY = REPOSITORY_ROOT / "db" / "migrations"


def main() -> None:
    """Run each SQL migration in one database transaction."""
    load_dotenv(REPOSITORY_ROOT / ".env")

    required_settings = ("DB_HOST", "DB_NAME", "DB_USER")
    missing_settings = [
        name for name in required_settings if not os.getenv(name, "").strip()
    ]
    if missing_settings:
        names = ", ".join(missing_settings)
        raise RuntimeError(f"Missing required database settings in .env: {names}")

    migrations = sorted(MIGRATIONS_DIRECTORY.glob("*.sql"), key=lambda path: path.name)
    if not migrations:
        raise RuntimeError(f"No SQL migrations found in {MIGRATIONS_DIRECTORY}")

    connection_settings = {
        "host": os.environ["DB_HOST"],
        "dbname": os.environ["DB_NAME"],
        "user": os.environ["DB_USER"],
        "port": int(os.getenv("DB_PORT", "5432")),
    }
    password = os.getenv("DB_PASSWORD")
    if password:
        connection_settings["password"] = password

    with psycopg.connect(**connection_settings) as connection:
        for migration in migrations:
            print(f"Running {migration.name}", flush=True)
            sql = migration.read_text(encoding="utf-8")
            connection.execute(sql, prepare=False)

    print(f"Applied {len(migrations)} migration(s).")


if __name__ == "__main__":
    main()
