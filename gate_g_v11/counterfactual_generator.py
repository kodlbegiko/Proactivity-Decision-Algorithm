from __future__ import annotations

from copy import deepcopy
from typing import Any

MUTATIONS = (
    ("permission", "missing"),
    ("information", "insufficient"),
    ("risk", "medium"),
    ("reversibility", "irreversible"),
    ("execution_possible", False),
    ("need", "optional"),
)


def mutate_act_state(state: dict[str, Any], index: int) -> tuple[dict[str, Any], str, Any]:
    out = deepcopy(state)
    factor, value = MUTATIONS[index % len(MUTATIONS)]
    out[factor] = value
    return out, factor, value
