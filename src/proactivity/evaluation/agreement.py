from __future__ import annotations

from collections import Counter
from typing import Sequence


def _check(a: Sequence[str], b: Sequence[str]) -> None:
    if len(a) != len(b):
        raise ValueError("label sequences must have equal length")
    if not a:
        raise ValueError("at least one paired label is required")


def raw_agreement(a: Sequence[str], b: Sequence[str]) -> float:
    _check(a, b)
    return sum(x == y for x, y in zip(a, b)) / len(a)


def cohen_kappa(a: Sequence[str], b: Sequence[str]) -> float:
    _check(a, b)
    n = len(a)
    observed = raw_agreement(a, b)
    ca, cb = Counter(a), Counter(b)
    labels = set(ca) | set(cb)
    expected = sum((ca[label] / n) * (cb[label] / n) for label in labels)
    if expected == 1.0:
        return 1.0 if observed == 1.0 else 0.0
    return (observed - expected) / (1.0 - expected)
