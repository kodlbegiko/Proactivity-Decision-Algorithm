from __future__ import annotations

import hashlib
import json
from pathlib import Path

from proactivity.specification import evaluate, load_spec, spec_sha256
from proactivity.specification.schema import enumerate_states, validate_state

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "spec/proactivity_policy_v2.json"
OUT = ROOT / "data/development/development_v2.jsonl"
SHA = ROOT / "data/development/development_v2.sha256"
DOMAINS = ("study", "work", "scheduling", "communication", "device", "travel")

CANONICAL = [
    {"permission":"not_required","information":"sufficient","urgency":"none","need":"none","side_effect":"none","risk":"low","reversibility":"reversible","deferral_available":False,"execution_possible":False,"clarification_possible":False,"acknowledged":False,"completed":False},
    {"permission":"not_required","information":"sufficient","urgency":"none","need":"material","side_effect":"none","risk":"low","reversibility":"reversible","deferral_available":True,"execution_possible":False,"clarification_possible":False,"acknowledged":False,"completed":False},
    {"permission":"not_required","information":"sufficient","urgency":"none","need":"optional","side_effect":"none","risk":"low","reversibility":"reversible","deferral_available":False,"execution_possible":False,"clarification_possible":False,"acknowledged":False,"completed":False},
    {"permission":"not_required","information":"sufficient","urgency":"high","need":"material","side_effect":"none","risk":"low","reversibility":"reversible","deferral_available":False,"execution_possible":False,"clarification_possible":False,"acknowledged":False,"completed":False},
    {"permission":"missing","information":"sufficient","urgency":"normal","need":"material","side_effect":"external","risk":"low","reversibility":"reversible","deferral_available":False,"execution_possible":True,"clarification_possible":False,"acknowledged":False,"completed":False},
    {"permission":"granted","information":"sufficient","urgency":"none","need":"material","side_effect":"external","risk":"low","reversibility":"reversible","deferral_available":False,"execution_possible":True,"clarification_possible":False,"acknowledged":False,"completed":False},
]


def key(state: dict) -> str:
    return hashlib.sha256(json.dumps(state, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def record(state: dict, index: int, spec: dict, sha: str) -> dict:
    result = evaluate(state, spec_path=SPEC)
    if result.status != "VALID_DECISION":
        raise RuntimeError(result)
    return {
        "scenario_id": "dv2-" + key(state)[:16],
        "domain": DOMAINS[index % len(DOMAINS)],
        "generator_role": "hash_sample_or_reachability",
        "state": state,
        "oracle_action": result.action,
        "matched_rule": result.matched_rule,
        "spec_version": spec["schema_version"],
        "spec_sha256": sha,
    }


def main() -> None:
    spec = load_spec(SPEC)
    sha = spec_sha256(SPEC)
    valid = [state for state in enumerate_states(spec) if validate_state(spec, state).valid]
    chosen = sorted(valid, key=key)[:294]
    seen = {key(state) for state in chosen}
    for state in CANONICAL:
        if key(state) not in seen:
            chosen.append(state)
            seen.add(key(state))
    chosen = sorted(chosen, key=key)
    rows = [record(state, index, spec, sha) for index, state in enumerate(chosen)]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)
    OUT.write_text(text, encoding="utf-8")
    digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
    SHA.write_text(
        f"{digest}  data/development/development_v2.jsonl\n{sha}  spec/proactivity_policy_v2.json\n",
        encoding="utf-8",
    )
    print(json.dumps({"generated": len(rows), "actions": sorted({row["oracle_action"] for row in rows}), "spec_sha256": sha, "dataset_sha256": digest}, sort_keys=True))


if __name__ == "__main__":
    main()
