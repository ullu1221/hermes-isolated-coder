"""Basic tests for utils.format_bytes."""

from utils import format_bytes


def test_format_bytes_exact_kb():
    assert format_bytes(1024) == "1.00 KB"


def test_format_bytes_exact_mb():
    assert format_bytes(1024 * 1024) == "1.00 MB"


def test_format_bytes_exact_gb():
    assert format_bytes(1024 * 1024 * 1024) == "1.00 GB"


if __name__ == "__main__":
    test_format_bytes_exact_kb()
    test_format_bytes_exact_mb()
    test_format_bytes_exact_gb()
    print("All tests passed.")
