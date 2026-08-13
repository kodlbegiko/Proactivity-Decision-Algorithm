from __future__ import annotations
import argparse, json
from pathlib import Path
from proactivity.schema import Scenario

def validate(path: Path) -> list[Scenario]:
    scenarios=[]; seen=set()
    for lineno,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
        if not line.strip(): continue
        try: s=Scenario.from_dict(json.loads(line))
        except Exception as e: raise ValueError(f"{path}:{lineno}: {e}") from e
        if s.scenario_id in seen: raise ValueError(f"duplicate scenario_id: {s.scenario_id}")
        seen.add(s.scenario_id); scenarios.append(s)
    if not scenarios: raise ValueError("dataset is empty")
    return scenarios
if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("path", type=Path); p.add_argument("--require-raw-context", action="store_true"); a=p.parse_args()
    s=validate(a.path)
    if a.require_raw_context and any(x.raw_context is None for x in s): raise SystemExit("raw_context required but missing")
    print(f"VALID: {len(s)} scenarios; unique_ids={len({x.scenario_id for x in s})}")
