#!/usr/bin/env python3
"""Generate deterministic DEVELOPMENT_ONLY recovery-v3 datasets.

Gate-F material is neither imported nor read. Generation uses only the frozen
specification/oracle code already present at the Gate-E recovery base.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from proactivity.specification.oracle import evaluate as _frozen_evaluate

SEED = 20260815
ACTIONS = ("ACT", "ASK", "IGNORE", "NOTIFY", "SUGGEST", "WAIT")
DOMAINS = ("calendar", "messages", "files", "tasks", "travel", "system")
OUT = Path("data/recovery_v3_dev_ood")
VALUES = {
    "permission": ("not_required", "missing", "granted"),
    "information": ("sufficient", "insufficient", "contradictory"),
    "urgency": ("none", "normal", "high", "expired"),
    "need": ("none", "optional", "material"),
    "side_effect": ("none", "local", "external"),
    "risk": ("low", "medium", "high"),
    "reversibility": ("reversible", "irreversible"),
    "deferral_available": (False, True),
    "execution_possible": (False, True),
    "clarification_possible": (False, True),
    "acknowledged": (False, True),
    "completed": (False, True),
}
KEYS = tuple(VALUES)


def oracle_action(state: dict[str, Any]) -> str | None:
    result = _frozen_evaluate(state)
    return result.action if result.status == "VALID_DECISION" else None


def state_id(state: dict[str, Any]) -> str:
    raw = json.dumps(state, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()[:16]


LEX = {
"permission": {
 "not_required": ["No authorization is needed.", "The operation may proceed without seeking authorization.", "Authorization is unnecessary here.", "This does not require authorization."],
 "missing": ["Authorization is still needed.", "Permission is still outstanding.", "Approval has not arrived.", "Authorization is not yet granted."],
 "granted": ["Authorization has been granted.", "Approval is already in place.", "Permission is already secured.", "Authorization is not unavailable."],
},
"information": {
 "sufficient": ["Information is sufficient.", "Enough evidence is available.", "The necessary facts are settled.", "The record is complete enough."],
 "insufficient": ["Information is incomplete.", "Key facts are missing.", "There is not enough evidence.", "Necessary evidence has not arrived."],
 "contradictory": ["The facts remain in conflict.", "Evidence conflicts.", "The accounts do not agree.", "The record disagrees with itself."],
},
"urgency": {
 "none": ["There is no current urgency.", "There is no time pressure.", "Timing can wait.", "Nothing is time-sensitive now."],
 "normal": ["Urgency is normal.", "Ordinary timing applies.", "This is timely but not urgent.", "Normal time pressure applies."],
 "high": ["Urgency is high.", "This needs attention immediately.", "Time pressure is severe.", "This cannot safely wait."],
 "expired": ["The window has expired.", "The deadline has passed.", "It is already too late for the current window.", "The relevant period is over."],
},
"need": {
 "none": ["No intervention is needed.", "There is no current need to intervene.", "Nothing calls for intervention.", "Intervention need is absent."],
 "optional": ["Intervention is optional.", "An optional recommendation could help.", "Intervention is discretionary.", "Help would be nice but not necessary."],
 "material": ["Material intervention is needed.", "Substantive intervention is required.", "There is a material need to intervene.", "The situation calls for real intervention."],
},
"side_effect": {
 "none": ["No side effect is expected.", "There is no material side effect.", "Nothing outside the decision changes.", "Effect scope is none."],
 "local": ["The effect stays local.", "The local system would change.", "Impact is confined locally.", "Side effect scope is local."],
 "external": ["The effect reaches an external party.", "An outside system would change.", "Impact extends beyond the local system.", "Side effect scope is external."],
},
"risk": {
 "low": ["Risk is low.", "This is a low-risk outcome.", "Risk remains minimal.", "Risk stays low."],
 "medium": ["Risk is medium.", "This is a moderate-risk outcome.", "Risk is neither low nor high.", "Risk stays moderate."],
 "high": ["Risk is high.", "This is a high-risk outcome.", "Risk is substantial.", "Risk stays high."],
},
"reversibility": {
 "reversible": ["The change can be reversed.", "Reversal remains possible.", "The change is reversible.", "The change is not irreversible."],
 "irreversible": ["The change cannot be reversed.", "Reversal is impossible.", "The change is irreversible.", "It cannot be rolled back."],
},
"deferral_available": {
 False: ["No later trigger is defined.", "There is no scheduled follow-up trigger.", "No concrete future trigger exists.", "Deferral lacks a trigger."],
 True: ["A later trigger is defined.", "There is a scheduled follow-up trigger.", "A concrete future trigger exists.", "Deferral has a defined trigger."],
},
"execution_possible": {
 False: ["Execution is not possible.", "The action cannot be carried out now.", "The capability is unavailable.", "Execution is blocked."],
 True: ["Execution is possible.", "The action can be carried out now.", "The capability is available.", "Nothing blocks execution."],
},
"clarification_possible": {
 False: ["Clarification is not possible.", "The missing point cannot be clarified.", "No clarification channel is available.", "We cannot obtain clarification."],
 True: ["Clarification is possible.", "The missing point can be clarified.", "A clarification channel is available.", "We can ask for clarification."],
},
"acknowledged": {
 False: ["Acknowledgement is absent.", "The user has not acknowledged.", "Receipt has not been acknowledged.", "The notice remains unacknowledged."],
 True: ["Acknowledgement is present.", "The user has acknowledged.", "Receipt has been acknowledged.", "The notice was acknowledged."],
},
"completed": {
 False: ["The task is incomplete.", "The objective remains unresolved.", "Work is still unfinished.", "Completion has not happened."],
 True: ["The task is complete.", "The objective has been resolved.", "Work is already finished.", "The task is not incomplete."],
},
}
STYLES = {"train": ("direct", "indirect", "conversational"), "validation": ("verbose", "negated"), "ood": ("compressed", "distractor", "implicit", "reordered")}
STYLE_INDEX = {"direct": 0, "verbose": 0, "indirect": 1, "distractor": 1, "conversational": 2, "compressed": 2, "negated": 3, "implicit": 3, "reordered": 3}
DISTRACTORS = ("The interface theme is unchanged.", "A nearby unrelated record was archived yesterday.", "No formatting preference is relevant to this choice.", "The device battery level is ordinary.")


def render(state: dict[str, Any], style: str, salt: int) -> tuple[str, list[str]]:
    idx = STYLE_INDEX[style]
    clauses = [LEX[k][state[k]][idx] for k in KEYS]
    families = ["lexical_paraphrase", "multi_factor_composition"]
    if style in {"reordered", "distractor"}:
        rr = random.Random(SEED + salt); rr.shuffle(clauses); families.append("clause_order_shift")
    if style == "distractor":
        clauses.insert((salt % (len(clauses) + 1)), DISTRACTORS[salt % len(DISTRACTORS)]); families.append("distractor_injection")
    if style == "implicit": families.extend(["explicit_implicit_conversion", "synonym_family"])
    if style == "negated": families.append("negation_scope")
    if style in {"compressed", "verbose"}: families.append("temporal_reformulation")
    if style in {"conversational", "implicit"}: families.append("permission_phrasing")
    return " ".join(clauses), sorted(set(families))


def enumerate_states() -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for combo in itertools.product(*(VALUES[k] for k in KEYS)):
        state = dict(zip(KEYS, combo)); action = oracle_action(state)
        if action in ACTIONS: grouped[action].append(state)
    return grouped


def choose_sources() -> dict[str, dict[str, list[dict[str, Any]]]]:
    grouped = enumerate_states(); rng = random.Random(SEED); out = {}
    for action in ACTIONS:
        rows = list(grouped[action]); rng.shuffle(rows)
        if len(rows) < 60: raise RuntimeError(f"insufficient source states for {action}: {len(rows)}")
        out[action] = {"train": rows[:42], "validation": rows[42:51], "ood": rows[51:60]}
    return out


def record_for(state: dict[str, Any], action: str, split: str, style: str, n: int) -> dict[str, Any]:
    sid = state_id(state); observation, families = render(state, style, n)
    return {"record_id": f"{split}-{action.lower()}-{sid}-{style}", "source_state_id": sid, "split": split, "development_status": "DEVELOPMENT_ONLY", "domain": DOMAINS[(int(sid[:8], 16) + n) % len(DOMAINS)], "observation": observation, "gold_action": action, "render_style": style, "stress_families": families}


def one_factor_counterfactuals(sources):
    priority = ("completed", "need", "information", "clarification_possible", "permission", "risk", "reversibility", "urgency", "deferral_available", "execution_possible")
    pairs = []; seen = set()
    for action in ACTIONS:
        for base in sources[action]["ood"]:
            found = None
            for field in priority:
                for value in VALUES[field]:
                    if value == base[field]: continue
                    other = dict(base); other[field] = value; other_action = oracle_action(other)
                    if other_action and other_action != action:
                        key = (state_id(base), state_id(other), field)
                        if key not in seen: found = (other, other_action, field); seen.add(key); break
                if found: break
            if found:
                other, other_action, field = found; i = len(pairs)
                left_obs, _ = render(base, "implicit", 1000 + i); right_obs, _ = render(other, "reordered", 2000 + i)
                pairs.append({"pair_id": f"cf-{i:03d}", "development_status": "DEVELOPMENT_ONLY", "changed_factor": field, "left": {"source_state_id": state_id(base), "domain": DOMAINS[i % len(DOMAINS)], "observation": left_obs, "gold_action": action}, "right": {"source_state_id": state_id(other), "domain": DOMAINS[(i + 1) % len(DOMAINS)], "observation": right_obs, "gold_action": other_action}})
    return pairs


def invariance_pairs(sources):
    pairs = []
    for action in ACTIONS:
        for base in sources[action]["ood"]:
            i = len(pairs); a, _ = render(base, "compressed", 3000 + i); b, _ = render(base, "distractor", 4000 + i)
            pairs.append({"pair_id": f"inv-{i:03d}", "development_status": "DEVELOPMENT_ONLY", "source_state_id": state_id(base), "gold_action": action, "left": {"domain": DOMAINS[i % len(DOMAINS)], "observation": a}, "right": {"domain": DOMAINS[(i + 2) % len(DOMAINS)], "observation": b}})
    return pairs


def write_jsonl(path: Path, rows) -> None:
    path.write_text("".join(json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n" for r in rows), encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True); sources = choose_sources()
    public_rows = {"train": [], "validation": [], "ood": []}; private_rows = {"train": [], "validation": [], "ood": []}; counter = 0
    for action in ACTIONS:
        for split in ("train", "validation", "ood"):
            for state in sources[action][split]:
                for style in STYLES[split]:
                    public_rows[split].append(record_for(state, action, split, style, counter)); counter += 1
                private_rows[split].append({"source_state_id": state_id(state), "split": split, "gold_action": action, "state": state})
    for split in public_rows:
        public_rows[split].sort(key=lambda r: r["record_id"]); private_rows[split].sort(key=lambda r: r["source_state_id"])
        write_jsonl(OUT / f"{split}.jsonl", public_rows[split]); write_jsonl(OUT / f"{split}_private.jsonl", private_rows[split])
    cf = one_factor_counterfactuals(sources); inv = invariance_pairs(sources)
    write_jsonl(OUT / "counterfactual_relations.jsonl", cf); write_jsonl(OUT / "invariance_relations.jsonl", inv)
    summary = {"development_status": "DEVELOPMENT_ONLY", "seed": SEED, "source_states_per_action": {"train": 42, "validation": 9, "ood": 9}, "rows": {k: len(v) for k, v in public_rows.items()}, "action_distribution": {k: dict(Counter(r["gold_action"] for r in v)) for k, v in public_rows.items()}, "counterfactual_pairs": len(cf), "invariance_pairs": len(inv), "stress_families": sorted({f for rows in public_rows.values() for r in rows for f in r["stress_families"]} | {"minimal_pair", "invariance_pair"}), "gate_f_records_accessed": 0}
    (OUT / "generation_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    files = sorted(p for p in OUT.iterdir() if p.is_file() and p.name != "hash_manifest.json")
    (OUT / "hash_manifest.json").write_text(json.dumps({p.name: sha(p) for p in files}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
