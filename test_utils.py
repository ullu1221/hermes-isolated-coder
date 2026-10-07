"""Basic tests for utils.format_bytes and utils.parse_bytes."""

from utils import format_bytes, parse_bytes


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


def test_parse_bytes_exact_kb():
    assert parse_bytes("1.00 KB") == 1024


def test_parse_bytes_exact_mb():
    assert parse_bytes("1.00 MB") == 1024 * 1024


def test_parse_bytes_exact_gb():
    assert parse_bytes("1.00 GB") == 1024 * 1024 * 1024


def test_parse_bytes_exact_tb():
    assert parse_bytes("1.00 TB") == 1024 ** 4


def test_parse_bytes_exact_pb():
    assert parse_bytes("1.00 PB") == 1024 ** 5


def test_parse_bytes_half_mb():
    # 1.5 MB -> 1.5 * 1024^2 bytes
    assert parse_bytes("1.5 MB") == int(round(1.5 * 1024 * 1024))


def test_parse_bytes_500_kb():
    assert parse_bytes("500 KB") == 500 * 1024


def test_parse_bytes_100_b():
    assert parse_bytes("100 B") == 100


def test_parse_bytes_case_insensitive():
    assert parse_bytes("1.5 mb") == parse_bytes("1.5 MB")
    assert parse_bytes("500 kb") == parse_bytes("500 KB")


def test_parse_bytes_no_space():
    assert parse_bytes("500KB") == 500 * 1024


def test_parse_bytes_zero():
    assert parse_bytes("0.00 B") == 0


def test_parse_bytes_invalid_raises():
    try:
        parse_bytes("invalid")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_roundtrip():
    """format_bytes(parse_bytes(text)) should give a string close to original."""
    test_strings = ["1.00 KB", "500 KB", "1.5 MB", "2.75 GB", "1.00 PB", "0.00 B"]
    for s in test_strings:
        raw = parse_bytes(s)
        formatted = format_bytes(raw)
        # The formatted string may have slightly different decimal representation,
        # but the numeric value should be consistent.
        re_parsed = parse_bytes(formatted)
        assert re_parsed == parse_bytes(s), f"Roundtrip failed for {s}"


if __name__ == "__main__":
    test_format_bytes_exact_kb()
    test_format_bytes_exact_mb()
    test_format_bytes_exact_gb()
    test_format_bytes_exact_tb()
    test_format_bytes_exact_pb()
    test_parse_bytes_exact_kb()
    test_parse_bytes_exact_mb()
    test_parse_bytes_exact_gb()
    test_parse_bytes_exact_tb()
    test_parse_bytes_exact_pb()
    test_parse_bytes_half_mb()
    test_parse_bytes_500_kb()
    test_parse_bytes_100_b()
    test_parse_bytes_case_insensitive()
    test_parse_bytes_no_space()
    test_parse_bytes_zero()
    test_parse_bytes_invalid_raises()
    test_roundtrip()
    print("All tests passed.")