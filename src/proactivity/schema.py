from __future__ import annotations
from dataclasses import dataclass,field
from datetime import datetime
from typing import Any
from .decisions import Decision
def _unit(name:str,value:float)->float:
    value=float(value)
    if not 0.0<=value<=1.0: raise ValueError(f"{name} must be in [0, 1], got {value}")
    return value
@dataclass(frozen=True)
class RawContext:
    current_activity:str; event_summary:str; observable_facts:tuple[str,...]; recent_history:tuple[str,...]=field(default_factory=tuple); permission_evidence:str="unknown"; time_context:str=""; source_kind:str="system_observation"
    @classmethod
    def from_dict(cls,data:dict[str,Any])->"RawContext":
        facts=tuple(str(x).strip() for x in data.get("observable_facts",[]))
        if not facts or any(not x for x in facts): raise ValueError("raw_context.observable_facts must contain non-empty facts")
        return cls(str(data["current_activity"]).strip(),str(data["event_summary"]).strip(),facts,tuple(str(x).strip() for x in data.get("recent_history",[])),str(data.get("permission_evidence","unknown")).strip(),str(data.get("time_context","")).strip(),str(data.get("source_kind","system_observation")).strip())
@dataclass(frozen=True)
class UserState:
    activity:str; workload:float; interruptibility:float
    @classmethod
    def from_dict(cls,data): return cls(str(data["activity"]),_unit("user_state.workload",data["workload"]),_unit("user_state.interruptibility",data["interruptibility"]))
@dataclass(frozen=True)
class Event:
    type:str; importance:float; urgency:float; deadline_seconds:int|None; confidence:float; evidence_reliability:float
    @classmethod
    def from_dict(cls,data):
        deadline=data.get("deadline_seconds")
        if deadline is not None:
            deadline=int(deadline)
            if deadline<0: raise ValueError("event.deadline_seconds must be >= 0 or null")
        return cls(str(data["type"]),_unit("event.importance",data["importance"]),_unit("event.urgency",data["urgency"]),deadline,_unit("event.confidence",data["confidence"]),_unit("event.evidence_reliability",data["evidence_reliability"]))
@dataclass(frozen=True)
class TaskState:
    status:str; acknowledged:bool; completed:bool
    @classmethod
    def from_dict(cls,data): return cls(str(data.get("status","unknown")),bool(data.get("acknowledged",False)),bool(data.get("completed",False)))
@dataclass(frozen=True)
class Scenario:
    scenario_id:str; timestamp:datetime; domain:str; raw_context:RawContext|None; user_state:UserState; event:Event; task_state:TaskState; history:tuple[dict[str,Any],...]=field(default_factory=tuple); action_risk:float=0.0; reversibility:float=1.0; expected_delay_cost:float=0.0; permission_required:bool=False; permission_granted:bool=False; context_freshness:float=1.0; candidate_decisions:tuple[Decision,...]=tuple(Decision)
    @classmethod
    def from_dict(cls,data):
        sid=str(data["scenario_id"]).strip()
        if not sid: raise ValueError("scenario_id must be non-empty")
        timestamp=datetime.fromisoformat(str(data["timestamp"]).replace("Z","+00:00")); decisions=tuple(Decision(x) for x in data.get("candidate_decisions",[d.value for d in Decision]))
        if len(set(decisions))!=len(decisions): raise ValueError("candidate_decisions must not contain duplicates")
        raw=RawContext.from_dict(data["raw_context"]) if "raw_context" in data else None
        obj=cls(sid,timestamp,str(data["domain"]),raw,UserState.from_dict(data["user_state"]),Event.from_dict(data["event"]),TaskState.from_dict(data.get("task_state",{})),tuple(data.get("history",[])),_unit("action_risk",data.get("action_risk",0.0)),_unit("reversibility",data.get("reversibility",1.0)),_unit("expected_delay_cost",data.get("expected_delay_cost",0.0)),bool(data.get("permission_required",False)),bool(data.get("permission_granted",False)),_unit("context_freshness",data.get("context_freshness",1.0)),decisions)
        obj.validate_safety_consistency(); return obj
    def validate_safety_consistency(self):
        if self.permission_granted and not self.permission_required: raise ValueError("permission_granted=true requires permission_required=true")
