from __future__ import annotations
import csv, json, random
from pathlib import Path

FIELDS=["scenario_id","domain","timestamp","scenario_context","preferred_action","acceptable_actions","confidence","ambiguity_flag","reason_code","criticality","rationale"]

def render(r):
    c=r["raw_context"]
    parts=[f"Current activity: {c['current_activity']}",f"Event: {c['event_summary']}","Observable facts: "+" | ".join(c['observable_facts'])]
    if c.get("recent_history"): parts.append("Recent history: "+" | ".join(c["recent_history"]))
    parts.append("Permission evidence: "+c.get("permission_evidence","unknown"))
    if c.get("time_context"): parts.append("Time context: "+c["time_context"])
    return "\n".join(parts)

def main():
    root=Path(__file__).resolve().parents[1]
    rows=[json.loads(x) for x in (root/"data/development/development_v1.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    outdir=root/"annotation"; outdir.mkdir(exist_ok=True)
    for name,seed in [("packet_a.csv",111),("packet_b.csv",222)]:
        arr=list(rows); random.Random(seed).shuffle(arr)
        with (outdir/name).open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=FIELDS); w.writeheader()
            for r in arr:
                w.writerow({"scenario_id":r["scenario_id"],"domain":r["domain"],"timestamp":r["timestamp"],"scenario_context":render(r)})
    print(f"packets=2 scenarios_each={len(rows)}")

if __name__=="__main__": main()
