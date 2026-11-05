from __future__ import annotations

import pytest

from tests.conftest import WORK_DATABASE, clone_work_database


@pytest.mark.parametrize("database_name", ["smartcrm", "smartcrm_test", "postgres"])
def test_work_database_guard_rejects_other_names(database_name: str) -> None:
    with pytest.raises(RuntimeError, match="smartcrm_work_test"):
        clone_work_database(database_name)
