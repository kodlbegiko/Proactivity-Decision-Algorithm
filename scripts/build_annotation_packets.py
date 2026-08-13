from __future__ import annotations
import argparse,csv,json,random
from pathlib import Path

FIELDS=["scenario_id","domain","timestamp","scenario_context","preferred_action","acceptable_actions","confidence","ambiguity_flag","reason_code","criticality","rationale"]
SOURCE_FIELDS=["scenario_id","domain","timestamp","scenario_context"]
ANNOTATION_FIELDS=[x for x in FIELDS if x not in SOURCE_FIELDS]

def render(r):
    c=r["raw_context"]
    parts=[f"Current activity: {c['current_activity']}",f"Event: {c['event_summary']}","Observable facts: "+" | ".join(c['observable_facts'])]
    if c.get("recent_history"): parts.append("Recent history: "+" | ".join(c["recent_history"]))
    parts.append("Permission evidence: "+c.get("permission_evidence","unknown"))
    if c.get("time_context"): parts.append("Time context: "+c["time_context"])
    return "\n".join(parts)

def load_packet(path):
    with path.open(newline="",encoding="utf-8") as f:
        reader=csv.reader(f)
        try: header=next(reader)
        except StopIteration as e: raise ValueError(f"empty packet: {path}") from e
        if header!=FIELDS: raise ValueError(f"packet schema mismatch: {path}")
        if len(header)!=len(set(header)): raise ValueError(f"duplicate packet headers: {path}")
        raw=list(reader)
    rows=[]
    for n,values in enumerate(raw,2):
        if len(values)!=len(header): raise ValueError(f"{path}:{n}: wrong column count")
        rows.append(dict(zip(header,values)))
    ids=[r["scenario_id"] for r in rows]
    if len(ids)!=len(set(ids)): raise ValueError(f"duplicate scenario_id in {path}")
    return rows

def validate(root):
    dev=[json.loads(x) for x in (root/"data/development/development_v1.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    dm={r["scenario_id"]:r for r in dev}
    if len(dev)!=144 or len(dm)!=144: raise ValueError("development_v1 must contain 144 unique scenarios")
    packets=[]
    for name in ("packet_a.csv","packet_b.csv"):
        rows=load_packet(root/"annotation"/name); pm={r["scenario_id"]:r for r in rows}
        if len(rows)!=144 or set(pm)!=set(dm): raise ValueError(f"{name}: scenario set mismatch")
        for sid,r in pm.items():
            d=dm[sid]; expected={"scenario_id":sid,"domain":d["domain"],"timestamp":d["timestamp"],"scenario_context":render(d)}
            if any(r[k]!=v for k,v in expected.items()): raise ValueError(f"{name}:{sid}: source context mismatch")
            if any(r[k].strip() for k in ANNOTATION_FIELDS): raise ValueError(f"{name}:{sid}: blank packet contains annotation data")
        packets.append(rows)
    if [r["scenario_id"] for r in packets[0]]==[r["scenario_id"] for r in packets[1]]: raise ValueError("packet A/B ordering must differ")
    return {"packet_a_rows":144,"packet_b_rows":144,"same_scenario_set":True,"different_order":True,"hidden_metadata_exposed":False,"researcher_scalars_exposed":False,"validation":"PASS"}

def generate(root):
    rows=[json.loads(x) for x in (root/"data/development/development_v1.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    outdir=root/"annotation"; outdir.mkdir(exist_ok=True)
    for name,seed in [("packet_a.csv",111),("packet_b.csv",222)]:
        arr=list(rows); random.Random(seed).shuffle(arr)
        with (outdir/name).open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=FIELDS); w.writeheader()
            for r in arr: w.writerow({"scenario_id":r["scenario_id"],"domain":r["domain"],"timestamp":r["timestamp"],"scenario_context":render(r)})
    print(f"packets=2 scenarios_each={len(rows)}")

def main():
    p=argparse.ArgumentParser(); p.add_argument("--validate-only",action="store_true"); args=p.parse_args(); root=Path(__file__).resolve().parents[1]
    if args.validate_only: print(json.dumps(validate(root),indent=2,sort_keys=True))
    else: generate(root)

if __name__=="__main__": main()
