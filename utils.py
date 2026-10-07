"""Utility functions for common tasks."""

import re


def format_bytes(size: int) -> str:
    """Convert raw bytes to a human-readable string (KB, MB, GB, TB, PB).

    Args:
        size: Size in bytes.

    Returns:
        Human-readable string like "1.00 KB", "2.50 MB", "1.00 GB", "1.00 TB", "1.00 PB".
    """
    if size < 0:
        raise ValueError("size must be non-negative")

    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    unit_index = 0
    size_float = float(size)

    while size_float >= 1024 and unit_index < len(units) - 1:
        size_float /= 1024
        unit_index += 1

    return f"{size_float:.2f} {units[unit_index]}"


def parse_bytes(text: str) -> int:
    """Convert a human-readable byte string back to raw bytes.

    Args:
        text: String like "1.5 MB", "500 KB", "1 GB", "100 B", etc.

    Returns:
        Size in bytes as an integer.

    Raises:
        ValueError: If the format is invalid.
    """
    # Remove any whitespace and convert to uppercase for case-insensitive matching
    text = text.strip().upper()

    # Pattern: number (integer or decimal) followed by optional space and unit (B, KB, MB, GB, TB, PB)
    match = re.match(r'^(\d+(?:\.\d+)?)\s*(B|KB|MB|GB|TB|PB)$', text)
    if not match:
        raise ValueError(f"Invalid byte format: {text}")

    size = float(match.group(1))
    unit = match.group(2)

    multipliers = {
        "B": 1,
        "KB": 1024,
        "MB": 1024**2,
        "GB": 1024**3,
        "TB": 1024**4,
        "PB": 1024**5,
    }

    bytes_val = size * multipliers[unit]
    return int(round(bytes_val))