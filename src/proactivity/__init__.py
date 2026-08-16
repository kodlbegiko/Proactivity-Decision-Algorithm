"""Core research types for the Proactivity Decision Algorithm mission."""

from .decisions import Decision
from .schema import Scenario

# Candidate-v7 retry 001: load the narrowly scoped pre-evaluation regex repair.
# The repair is frozen as part of the Candidate-v7 source lineage and is
# documented in gate_recovery_v7/infrastructure_retry_001.json.
from . import candidate_v7_recovery_patch as _candidate_v7_recovery_patch

__all__ = ["Decision", "Scenario"]
