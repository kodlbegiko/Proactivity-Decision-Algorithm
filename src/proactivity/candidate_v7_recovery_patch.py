"""Candidate-v7 infrastructure-retry patch for a pre-evaluation regex typo.

This module is deliberately narrow: it corrects one implementation typo found by
source unit tests before any generated dataset, validation metric, or
qualification metric existed. It does not change architecture families,
configuration values, thresholds, seeds, dataset sizes, or selection rules.
"""

from . import candidate_v7 as _candidate_v7

_BAD = r"information\s+is\s+(?:not\s+)?sufficient"
_FIXED = r"information\s+is\s+(?:not\s+sufficient|insufficient)"

_repaired = []
for _value, _patterns in _candidate_v7.PATTERNS["information"]:
    if _value == "insufficient":
        _patterns = tuple(_FIXED if pattern == _BAD else pattern for pattern in _patterns)
    _repaired.append((_value, _patterns))
_candidate_v7.PATTERNS["information"] = tuple(_repaired)
