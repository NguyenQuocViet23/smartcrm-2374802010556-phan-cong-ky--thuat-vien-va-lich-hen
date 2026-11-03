import pytest

from tests.conftest import validate_test_database


def test_database_guard_rejects_smartcrm() -> None:
    with pytest.raises(RuntimeError, match="Từ chối chạy: tên database phải kết thúc bằng _test"):
        validate_test_database("postgresql://postgres@localhost:5432/smartcrm")


def test_database_guard_accepts_smartcrm_test() -> None:
    assert validate_test_database("postgresql://postgres@localhost:5432/smartcrm_test") == "smartcrm_test"
