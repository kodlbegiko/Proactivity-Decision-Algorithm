from __future__ import annotations
import csv,hashlib,json,shutil
from dataclasses import dataclass
from pathlib import Path
from ..decisions import Decision
ALLOWED_REASON_CODES={"no_expected_value","timing","interruption_cost","missing_context","permission","risk","redundant","stale_context","delay_cost","criticality","other"}
SOURCE_FIELDS=("scenario_id","domain","timestamp","scenario_context")
ANNOTATION_FIELDS=("preferred_action","acceptable_actions","confidence","ambiguity_flag","reason_code","criticality","rationale")
PACKET_FIELDS=SOURCE_FIELDS+ANNOTATION_FIELDS
@dataclass(frozen=True)
class Annotation:
    scenario_id:str; preferred_action:Decision; acceptable_actions:frozenset[Decision]; confidence:int; ambiguity_flag:bool; reason_code:str; criticality:str
def parse_annotation_row(row:dict[str,str])->Annotation:
    sid=row.get("scenario_id","").strip()
    if not sid: raise ValueError("scenario_id is required")
    preferred=Decision(row.get("preferred_action","").strip())
    parts=[x.strip() for x in row.get("acceptable_actions","").split("|") if x.strip()]
    if len(parts)!=len(set(parts)): raise ValueError("acceptable_actions must not contain duplicates")
    acceptable=frozenset(Decision(x) for x in parts)
    if not acceptable: raise ValueError("acceptable_actions must not be empty")
    if preferred not in acceptable: raise ValueError("preferred_action must be in acceptable_actions")
    confidence=int(row.get("confidence","0"))
    if not 1<=confidence<=5: raise ValueError("confidence must be 1..5")
    ambiguity=row.get("ambiguity_flag","").strip()
    if ambiguity not in {"true","false"}: raise ValueError("ambiguity_flag must be canonical true or false")
    reason=row.get("reason_code","").strip()
    if reason not in ALLOWED_REASON_CODES: raise ValueError(f"unknown reason_code: {reason}")
    criticality=row.get("criticality","").strip().upper()
    if criticality not in {"NONE","IMPORTANT","CRITICAL"}: raise ValueError("criticality must be NONE, IMPORTANT, or CRITICAL")
    return Annotation(sid,preferred,acceptable,confidence,ambiguity=="true",reason,criticality)
def _read_csv_strict(path:str|Path)->tuple[list[str],list[dict[str,str]]]:
    with Path(path).open(newline="",encoding="utf-8") as f:
        reader=csv.reader(f)
        try: header=next(reader)
        except StopIteration as e: raise ValueError("empty annotation CSV") from e
        if len(header)!=len(set(header)): raise ValueError("duplicate CSV headers")
        raw=list(reader)
    rows=[]
    for lineno,values in enumerate(raw,2):
        if len(values)!=len(header): raise ValueError(f"row {lineno} column count differs from header")
        rows.append(dict(zip(header,values)))
    return header,rows
def load_annotations(path:str|Path)->list[Annotation]:
    _,rows=_read_csv_strict(path); annotations=[parse_annotation_row(row) for row in rows]; ids=[a.scenario_id for a in annotations]
    if len(ids)!=len(set(ids)): raise ValueError("duplicate scenario_id in annotation file")
    return annotations
def validate_completed_annotations(completed:str|Path,blank_packet:str|Path,expected_count:int=144)->dict:
    bh,br=_read_csv_strict(blank_packet); ch,cr=_read_csv_strict(completed)
    if tuple(bh)!=PACKET_FIELDS or tuple(ch)!=PACKET_FIELDS or bh!=ch: raise ValueError("annotation schema differs from frozen packet")
    def index(rows,name):
        out={}
        for row in rows:
            sid=row.get("scenario_id","").strip()
            if not sid or sid in out: raise ValueError(f"{name}: blank or duplicate scenario_id: {sid}")
            out[sid]=row
        return out
    blank,done=index(br,"blank"),index(cr,"completed")
    if len(blank)!=expected_count or len(done)!=expected_count or set(blank)!=set(done): raise ValueError(f"completed annotation must contain exactly the frozen {expected_count} scenario set")
    for sid in sorted(done):
        for field in SOURCE_FIELDS:
            if done[sid][field]!=blank[sid][field]: raise ValueError(f"ANNOTATION_INPUT_INVALID — SOURCE_CONTEXT_MODIFIED: {sid}:{field}")
        for field in ANNOTATION_FIELDS[:-1]:
            if not done[sid].get(field,"").strip(): raise ValueError(f"{sid}: required annotation field blank: {field}")
        parse_annotation_row(done[sid])
    return {"scenario_count":len(done),"validation":"PASS"}
def sha256_file(path:str|Path)->str:
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""): h.update(chunk)
    return h.hexdigest()
def archive_raw_annotations(a:str|Path,b:str|Path,packet_a:str|Path,packet_b:str|Path,out_dir:str|Path="annotations/raw")->dict:
    va=validate_completed_annotations(a,packet_a); vb=validate_completed_annotations(b,packet_b); out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    ta,tb,sums,manifest=out/"annotator_a_v1.csv",out/"annotator_b_v1.csv",out/"SHA256SUMS",out/"manifest.json"
    existing=[str(p) for p in (ta,tb,sums,manifest) if p.exists()]
    if existing: raise FileExistsError(f"immutable raw archive already exists: {existing}")
    shutil.copyfile(a,ta); shutil.copyfile(b,tb); ha,hb=sha256_file(ta),sha256_file(tb)
    sums.write_text(f"{ha}  annotator_a_v1.csv\n{hb}  annotator_b_v1.csv\n",encoding="utf-8")
    data={"schema_version":1,"privacy":"public manifest contains no annotator identity","annotator_a":{"filename":ta.name,"sha256":ha,"scenario_count":va["scenario_count"]},"annotator_b":{"filename":tb.name,"sha256":hb,"scenario_count":vb["scenario_count"]}}
    manifest.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n",encoding="utf-8"); return data
