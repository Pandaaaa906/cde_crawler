from typing import List


def first(l: List, default=None):
    if not l:
        return default
    return l[0]


def strip(s: str):
    if isinstance(s, str):
        return s.strip()
    return s
