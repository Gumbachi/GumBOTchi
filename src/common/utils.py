"""Utility functions that are used in multiple places"""

from typing import Any


def chunk(arr: list[Any], chunksize: int) -> list[list[Any]]:
    """Split a list into a list of lists of a specific size"""
    return [arr[i : i + chunksize] for i in range(0, len(arr), chunksize)]


def ellipsize(text: str, maxsize: int = 64) -> str:
    """Shrink a string to a certain size and ellipsize it"""
    if len(text) < maxsize:
        return text
    return text[:maxsize] + "..."
