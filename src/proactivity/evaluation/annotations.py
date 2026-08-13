from __future__ import annotations
import csv
from dataclasses import dataclass
from pathlib import Path
from ..decisions import Decision
ALLOWED_REASON_CODES={"no_expected_value","timing","interruption_cost","missing_context","permission","risk","redundant","stale_context","delay_cost","criticality","other"}
@dataclass(frozen=True)
class Annotation:
    scenario_id:str; preferred_action:Decision; acceptable_actions:frozenset[Decision]; confidence:int; ambiguity_flag:bool; reason_code:str; criticality:str
def parse_annotation_row(row:dict[str,str])->Annotation:
    sid=row.get("scenario_id","").strip()
    if not sid: raise ValueError("scenario_id is required")
    preferred=Decision(row.get("preferred_action","").strip())
    parts=[x.strip() for x in row.get("acceptable_actions","").split("|") if x.strip()]; acceptable=frozenset(Decision(x) for x in parts)
    if not acceptable: raise ValueError("acceptable_actions must not be empty")
    if preferred not in acceptable: raise ValueError("preferred_action must be in acceptable_actions")
    confidence=int(row.get("confidence","0"))
    if not 1<=confidence<=5: raise ValueError("confidence must be 1..5")
    ambiguity=row.get("ambiguity_flag","").strip().lower()
    if ambiguity not in {"true","false"}: raise ValueError("ambiguity_flag must be true or false")
    reason=row.get("reason_code","").strip()
    if reason not in ALLOWED_REASON_CODES: raise ValueError(f"unknown reason_code: {reason}")
    criticality=row.get("criticality","").strip().upper()
    if criticality not in {"NONE","IMPORTANT","CRITICAL"}: raise ValueError("criticality must be NONE, IMPORTANT, or CRITICAL")
    return Annotation(sid,preferred,acceptable,confidence,ambiguity=="true",reason,criticality)
def load_annotations(path:str|Path)->list[Annotation]:
    with Path(path).open(newline="",encoding="utf-8") as f: rows=list(csv.DictReader(f))
    annotations=[parse_annotation_row(row) for row in rows]; ids=[a.scenario_id for a in annotations]
    if len(ids)!=len(set(ids)): raise ValueError("duplicate scenario_id in annotation file")
    return annotations
