"""Utility functions for common tasks."""


def format_bytes(size: int) -> str:
    """Convert raw bytes to a human-readable string (KB, MB, GB).

    Args:
        size: Size in bytes.

    Returns:
        Human-readable string like "1.00 KB", "2.50 MB", "1.00 GB".
    """
    if size < 0:
        raise ValueError("size must be non-negative")

    units = ["B", "KB", "MB", "GB"]
    unit_index = 0
    size_float = float(size)

    while size_float >= 1024 and unit_index < len(units) - 1:
        size_float /= 1024
        unit_index += 1

    return f"{size_float:.2f} {units[unit_index]}"
