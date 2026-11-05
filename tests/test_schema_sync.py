import re
from difflib import unified_diff
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def normalize_ddl(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"--.*?$", "", text, flags=re.MULTILINE)
    statements = [statement.strip() for statement in text.split(";") if statement.strip()]
    normalized = []
    for statement in statements:
        statement = re.sub(r"\s+", " ", statement).strip().lower()
        # IF NOT EXISTS is intentional: schema.sql creates a new database,
        # while the migration must be safe to run repeatedly.
        statement = re.sub(
            r"\b(create\s+(?:table|index))\s+if\s+not\s+exists\b",
            r"\1",
            statement,
        )
        if statement:
            normalized.append(statement)
    return normalized


def _statements(path: Path) -> list[str]:
    statements = normalize_ddl(path)
    return statements or []


def ddl_diff(expected: list[str], actual: list[str]) -> str:
    return "\n".join(
        unified_diff(
            [f"{statement};" for statement in expected],
            [f"{statement};" for statement in actual],
            lineterm="",
        )
    )


def test_schema_and_migration_have_the_same_ddl() -> None:
    schema = ROOT / "db" / "schema.sql"
    migration = ROOT / "db" / "migrations" / "001_create_tables.sql"
    expected = _statements(schema)
    actual = _statements(migration)

    diff = ddl_diff(expected, actual)
    assert not diff, "db/schema.sql và migration không đồng bộ:\n" + diff


def test_ddl_comparison_detects_added_column() -> None:
    expected = ["create table technician (technician_id bigint primary key)"]
    actual = ["create table technician (technician_id bigint primary key, is_active boolean)"]

    assert ddl_diff(expected, actual)
