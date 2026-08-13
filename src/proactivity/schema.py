from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .decisions import Decision


def _unit(name: str, value: float) -> float:
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be in [0, 1], got {value}")
    return value


@dataclass(frozen=True)
class UserState:
    activity: str
    workload: float
    interruptibility: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserState":
        return cls(
            activity=str(data["activity"]),
            workload=_unit("user_state.workload", data["workload"]),
            interruptibility=_unit("user_state.interruptibility", data["interruptibility"]),
        )


@dataclass(frozen=True)
class Event:
    type: str
    importance: float
    urgency: float
    deadline_seconds: int | None
    confidence: float
    evidence_reliability: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Event":
        deadline = data.get("deadline_seconds")
        if deadline is not None:
            deadline = int(deadline)
            if deadline < 0:
                raise ValueError("event.deadline_seconds must be >= 0 or null")
        return cls(
            type=str(data["type"]),
            importance=_unit("event.importance", data["importance"]),
            urgency=_unit("event.urgency", data["urgency"]),
            deadline_seconds=deadline,
            confidence=_unit("event.confidence", data["confidence"]),
            evidence_reliability=_unit("event.evidence_reliability", data["evidence_reliability"]),
        )


@dataclass(frozen=True)
class TaskState:
    status: str
    acknowledged: bool
    completed: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskState":
        return cls(
            status=str(data.get("status", "unknown")),
            acknowledged=bool(data.get("acknowledged", False)),
            completed=bool(data.get("completed", False)),
        )


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    timestamp: datetime
    domain: str
    user_state: UserState
    event: Event
    task_state: TaskState
    history: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    action_risk: float = 0.0
    reversibility: float = 1.0
    expected_delay_cost: float = 0.0
    permission_required: bool = False
    permission_granted: bool = False
    context_freshness: float = 1.0
    candidate_decisions: tuple[Decision, ...] = tuple(Decision)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Scenario":
        sid = str(data["scenario_id"]).strip()
        if not sid:
            raise ValueError("scenario_id must be non-empty")
        timestamp = datetime.fromisoformat(str(data["timestamp"]).replace("Z", "+00:00"))
        decisions = tuple(Decision(x) for x in data.get("candidate_decisions", [d.value for d in Decision]))
        if len(set(decisions)) != len(decisions):
            raise ValueError("candidate_decisions must not contain duplicates")
        return cls(
            scenario_id=sid,
            timestamp=timestamp,
            domain=str(data["domain"]),
            user_state=UserState.from_dict(data["user_state"]),
            event=Event.from_dict(data["event"]),
            task_state=TaskState.from_dict(data.get("task_state", {})),
            history=tuple(data.get("history", [])),
            action_risk=_unit("action_risk", data.get("action_risk", 0.0)),
            reversibility=_unit("reversibility", data.get("reversibility", 1.0)),
            expected_delay_cost=_unit("expected_delay_cost", data.get("expected_delay_cost", 0.0)),
            permission_required=bool(data.get("permission_required", False)),
            permission_granted=bool(data.get("permission_granted", False)),
            context_freshness=_unit("context_freshness", data.get("context_freshness", 1.0)),
            candidate_decisions=decisions,
        )

    def validate_safety_consistency(self) -> None:
        if self.permission_granted and not self.permission_required:
            raise ValueError("permission_granted=true requires permission_required=true")
