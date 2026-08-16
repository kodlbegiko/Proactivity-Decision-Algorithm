from __future__ import annotations

from enum import Enum

class Decision(str, Enum):
    IGNORE="IGNORE"; WAIT="WAIT"; SUGGEST="SUGGEST"; NOTIFY="NOTIFY"; ASK="ASK"; ACT="ACT"
INTERVENTIONS=frozenset({Decision.SUGGEST,Decision.NOTIFY,Decision.ASK,Decision.ACT})
NON_INTERVENTIONS=frozenset({Decision.IGNORE,Decision.WAIT})
ORDER=tuple(Decision); INTENSITY={decision:i for i,decision in enumerate(ORDER)}
def is_intervention(decision:Decision|str)->bool: return Decision(decision) in INTERVENTIONS
def autonomous(decision:Decision|str)->bool: return Decision(decision) is Decision.ACT
def intensity(decision:Decision|str)->int: return INTENSITY[Decision(decision)]
