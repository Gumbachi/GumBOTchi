"""Utility functions that are used in multiple places"""


def chunk(arr: list, chunksize: int) -> list[list]:
    """Split a list into a list of lists of a specific size"""
    return [arr[i: i+chunksize] for i in range(0, len(arr), chunksize)]
