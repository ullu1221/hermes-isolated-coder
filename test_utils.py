"""Basic tests for utils.format_bytes."""

from utils import format_bytes


def test_format_bytes_exact_kb():
    assert format_bytes(1024) == "1.00 KB"


def test_format_bytes_exact_mb():
    assert format_bytes(1024 * 1024) == "1.00 MB"


def test_format_bytes_exact_gb():
    assert format_bytes(1024 * 1024 * 1024) == "1.00 GB"


def test_format_bytes_exact_tb():
    assert format_bytes(1024 ** 4) == "1.00 TB"


def test_format_bytes_exact_pb():
    assert format_bytes(1024 ** 5) == "1.00 PB"


if __name__ == "__main__":
    test_format_bytes_exact_kb()
    test_format_bytes_exact_mb()
    test_format_bytes_exact_gb()
    test_format_bytes_exact_tb()
    test_format_bytes_exact_pb()
    print("All tests passed.")