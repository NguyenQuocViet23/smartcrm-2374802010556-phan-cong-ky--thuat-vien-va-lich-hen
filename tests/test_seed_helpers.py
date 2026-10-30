"""Unit tests for deterministic CSV normalization helpers."""

import pytest

from scripts.seed_real_data import normalize_phone, normalize_status


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("0909 123 456", "0909123456"),
        ("+84 909.123.456", "0909123456"),
        ("84909123456", "0909123456"),
        ("", None),
        ("123456789", None),
    ],
)
def test_normalize_phone(source: str, expected: str | None) -> None:
    assert normalize_phone(source) == expected


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("DA_PHAN_CONG", "DA_PHAN_CONG"),
        ("ĐÃ_PHÂN_CÔNG", "DA_PHAN_CONG"),
        ("CHO_LINH_KIEN", "CHO_LINH_KIEN"),
        ("ĐANG_XỬ_LÝ", "DANG_XU_LY"),
        ("DA_DONG", "DA_DONG"),
    ],
)
def test_normalize_status_accepts_source_and_database_codes(
    source: str, expected: str
) -> None:
    assert normalize_status(source) == expected


def test_normalize_status_rejects_unknown_code() -> None:
    with pytest.raises(ValueError, match="Unsupported ticket status"):
        normalize_status("KHONG_HOP_LE")
