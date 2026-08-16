from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from proactivity.specification.oracle import evaluate, load_spec, spec_sha256
from proactivity.specification.schema import enumerate_states, validate_state

SEED = 20260816
ACTIONS = ("ACT", "ASK", "IGNORE", "NOTIFY", "SUGGEST", "WAIT")
FIELDS = (
    "permission",
    "information",
    "urgency",
    "need",
    "side_effect",
    "risk",
    "reversibility",
    "deferral_available",
    "execution_possible",
    "clarification_possible",
    "acknowledged",
    "completed",
)

SPLIT_SIZES = {
    "train": 3600,
    "validation": 900,
    "development_ood": 900,
    "lexical_holdout": 600,
    "rendering_holdout": 600,
    "compositional_holdout": 600,
    "negation": 360,
}
PAIR_SIZES = {"counterfactual": 180, "invariance": 180}

FAMILIES = {
    "train": ["direct_declarative", "conversational_dialogue", "email_issue_tracker", "compact_notes", "distractors"],
    "validation": ["direct_declarative", "conversational_dialogue", "email_issue_tracker", "compact_notes", "distractors"],
    "development_ood": ["implication", "consequence_description", "passive_voice", "reported_speech"],
    "lexical_holdout": ["direct_declarative", "compact_notes"],
    "rendering_holdout": ["long_form_narrative", "contrast_clauses", "temporal_clauses"],
    "compositional_holdout": ["conditional_statements", "contrast_clauses", "reported_speech", "distractors"],
    "negation": ["explicit_negation", "double_negation"],
}

# Canonical semantic statements. These are newly authored for Candidate-v6 and are
# intentionally independent of Candidate-v5 data / generators.
BASE: dict[str, dict[Any, str]] = {
    "permission": {
        "not_required": "No authorization is required for this operation",
        "missing": "Required authorization has not been obtained",
        "granted": "The required authorization has been granted",
    },
    "information": {
        "sufficient": "The available information is sufficient to decide",
        "insufficient": "Important information needed for a decision is still missing",
        "contradictory": "The available information contains unresolved contradictions",
    },
    "urgency": {
        "none": "There is no current time pressure",
        "normal": "The matter has ordinary time sensitivity",
        "high": "The matter is time-critical",
        "expired": "The relevant deadline has already passed",
    },
    "need": {
        "none": "There is no present need for intervention",
        "optional": "An intervention would be optional rather than necessary",
        "material": "A material intervention is presently needed",
    },
    "side_effect": {
        "none": "The intervention would create no material side effect",
        "local": "Any material side effect would remain local to the user or system",
        "external": "The intervention would create an external side effect",
    },
    "risk": {
        "low": "The operational risk is low",
        "medium": "The operational risk is moderate",
        "high": "The operational risk is high",
    },
    "reversibility": {
        "reversible": "The action can be reversed after execution",
        "irreversible": "The action cannot be reversed after execution",
    },
    "deferral_available": {
        False: "There is no defined opportunity to defer and revisit later",
        True: "A defined opportunity exists to defer and revisit later",
    },
    "execution_possible": {
        False: "The action cannot currently be executed",
        True: "The action can currently be executed",
    },
    "clarification_possible": {
        False: "No clarification can currently be requested",
        True: "Clarification can currently be requested",
    },
    "acknowledged": {
        False: "The relevant information has not been acknowledged",
        True: "The relevant information has already been acknowledged",
    },
    "completed": {
        False: "The underlying task is not complete",
        True: "The underlying task has already been completed",
    },
}

# Lexically isolated paraphrases reserved for lexical holdout only.
LEXICAL_HOLDOUT: dict[str, dict[Any, str]] = {
    "permission": {
        "not_required": "This step falls outside any consent requirement",
        "missing": "The needed go-ahead remains outstanding",
        "granted": "The necessary go-ahead is already in hand",
    },
    "information": {
        "sufficient": "The evidence on hand is adequate for a determination",
        "insufficient": "The evidence base still has a consequential gap",
        "contradictory": "The evidence base points in mutually incompatible directions",
    },
    "urgency": {
        "none": "Nothing is pressing on the clock",
        "normal": "Timing matters only in the ordinary course",
        "high": "The window for response is rapidly closing",
        "expired": "The applicable window has closed",
    },
    "need": {
        "none": "No intervention is called for at present",
        "optional": "Intervening is discretionary",
        "material": "A consequential intervention is called for now",
    },
    "side_effect": {
        "none": "Taking the step changes nothing material",
        "local": "Any consequential change stays within the local context",
        "external": "Taking the step changes something outside the local context",
    },
    "risk": {
        "low": "Exposure to harm is minimal",
        "medium": "Exposure to harm is neither trivial nor severe",
        "high": "Exposure to harm is substantial",
    },
    "reversibility": {
        "reversible": "The step can later be undone",
        "irreversible": "The step cannot later be undone",
    },
    "deferral_available": {
        False: "There is no later checkpoint available",
        True: "A later checkpoint is available",
    },
    "execution_possible": {
        False: "Execution is presently infeasible",
        True: "Execution is presently feasible",
    },
    "clarification_possible": {
        False: "There is no channel for obtaining clarification now",
        True: "A channel exists for obtaining clarification now",
    },
    "acknowledged": {
        False: "Receipt has not been confirmed",
        True: "Receipt has already been confirmed",
    },
    "completed": {
        False: "The underlying work remains unfinished",
        True: "The underlying work is finished",
    },
}

NEGATED: dict[str, dict[Any, str]] = {
    "permission": {
        "not_required": "It is not the case that authorization is required",
        "missing": "It is not true that the required authorization has been granted",
        "granted": "The required authorization is not missing; it has been granted",
    },
    "information": {
        "sufficient": "It is not true that decision-relevant information is missing or contradictory",
        "insufficient": "It is not true that all decision-relevant information is available",
        "contradictory": "The information is not mutually consistent",
    },
    "urgency": {
        "none": "The matter is not time-sensitive",
        "normal": "The timing is not absent and not extreme; it is ordinary",
        "high": "The matter is not safe to leave until the ordinary window",
        "expired": "The deadline is no longer pending because it has passed",
    },
    "need": {
        "none": "It is not the case that intervention is needed",
        "optional": "Intervention is not required, though it remains an option",
        "material": "It is not merely optional; a material intervention is needed",
    },
    "side_effect": {
        "none": "The step does not create a material side effect",
        "local": "The side effect is not external; it stays local",
        "external": "The side effect does not stay local; it reaches an external target",
    },
    "risk": {
        "low": "The risk is not medium or high; it is low",
        "medium": "The risk is neither low nor high; it is moderate",
        "high": "The risk is not low or moderate; it is high",
    },
    "reversibility": {
        "reversible": "The action is not irreversible; it can be undone",
        "irreversible": "The action is not reversible once performed",
    },
    "deferral_available": {
        False: "There is not a later deferral point available",
        True: "It is not true that deferral is unavailable; a later point exists",
    },
    "execution_possible": {
        False: "Execution is not currently possible",
        True: "Execution is not blocked; it is currently possible",
    },
    "clarification_possible": {
        False: "Clarification cannot currently be obtained",
        True: "Clarification is not unavailable; it can be obtained",
    },
    "acknowledged": {
        False: "The information has not been acknowledged",
        True: "The information is no longer unacknowledged",
    },
    "completed": {
        False: "The task has not been completed",
        True: "The task is not unfinished; it is complete",
    },
}

DISTRACTORS = (
    "The interface theme is currently set to dark mode",
    "A routine status heartbeat was received earlier",
    "The record contains an unrelated descriptive tag",
    "The current workspace contains several other inactive items",
)

TRANSITIONS: tuple[tuple[str, Any, Any], ...] = (
    ("permission", "granted", "missing"),
    ("information", "sufficient", "insufficient"),
    ("information", "sufficient", "contradictory"),
    ("risk", "low", "high"),
    ("reversibility", "reversible", "irreversible"),
    ("execution_possible", True, False),
    ("need", "material", "optional"),
    ("need", "material", "none"),
    ("deferral_available", True, False),
    ("acknowledged", False, True),
    ("completed", False, True),
    ("urgency", "none", "normal"),
    ("urgency", "normal", "high"),
    ("urgency", "high", "expired"),
)


@dataclass(frozen=True)
class Rendered:
    observation: str
    factor_evidence_map: dict[str, str]


def _clause(field: str, value: Any, *, split: str, family: str) -> str:
    if split == "lexical_holdout":
        text = LEXICAL_HOLDOUT[field][value]
    elif family in {"explicit_negation", "double_negation"}:
        text = NEGATED[field][value]
    else:
        text = BASE[field][value]

    if family == "implication":
        return f"From the current circumstances, it follows that {text[0].lower() + text[1:]}."
    if family == "consequence_description":
        return f"The practical consequence is this: {text}."
    if family == "passive_voice":
        return f"Current-state assessment: {text}."
    if family == "reported_speech":
        return f"The status report states that {text[0].lower() + text[1:]}."
    if family == "contrast_clauses":
        return f"Despite unrelated background details, {text[0].lower() + text[1:]}."
    if family == "temporal_clauses":
        return f"At the present decision point, {text[0].lower() + text[1:]}."
    if family == "conditional_statements":
        return f"For the decision now being considered, treat the following as the operative condition: {text}."
    if family == "double_negation":
        return f"After resolving the double-negative wording, {text[0].lower() + text[1:]}."
    return text + "."


def render_state(state: Mapping[str, Any], *, split: str, family: str, rng: random.Random) -> Rendered:
    evidence: dict[str, str] = {field: _clause(field, state[field], split=split, family=family) for field in FIELDS}
    fields = list(FIELDS)
    rng.shuffle(fields)
    clauses = [evidence[field] for field in fields]

    if family == "conversational_dialogue":
        body = "\n".join(f"Speaker {1 + (i % 2)}: {clause}" for i, clause in enumerate(clauses))
    elif family == "email_issue_tracker":
        body = "Subject: current intervention state\n\n" + "\n".join(f"- {clause}" for clause in clauses)
    elif family == "compact_notes":
        body = " | ".join(clause.rstrip(".") for clause in clauses) + "."
    elif family == "long_form_narrative":
        body = "Context review. " + " Meanwhile, ".join(clause.rstrip(".") for clause in clauses) + ". End of current-state review."
    elif family == "distractors":
        extras = rng.sample(list(DISTRACTORS), k=2)
        body_parts = clauses + [item + "." for item in extras]
        rng.shuffle(body_parts)
        body = " ".join(body_parts)
    elif family == "conditional_statements":
        half = max(1, len(clauses) // 2)
        body = "If the system evaluates the present case, use these conditions: " + " ".join(clauses[:half]) + " In addition, " + " ".join(clauses[half:])
    else:
        body = " ".join(clauses)
    return Rendered(body, evidence)


def _state_pools(spec: Mapping[str, Any]) -> dict[str, list[dict[str, Any]]]:
    pools: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for state in enumerate_states(spec):
        if not validate_state(spec, state).valid:
            continue
        result = evaluate(state, spec=spec)
        if result.status == "VALID_DECISION" and result.action in ACTIONS:
            pools[result.action].append(state)
    missing = [action for action in ACTIONS if not pools[action]]
    if missing:
        raise RuntimeError(f"oracle produced no valid states for actions: {missing}")
    return dict(pools)


def _balanced_rows(
    *,
    split: str,
    count: int,
    pools: Mapping[str, list[dict[str, Any]]],
    spec: Mapping[str, Any],
    rng: random.Random,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    per = count // len(ACTIONS)
    remainder = count % len(ACTIONS)
    for ai, action in enumerate(ACTIONS):
        target = per + (1 if ai < remainder else 0)
        pool = pools[action]
        for idx in range(target):
            state = dict(pool[rng.randrange(len(pool))])
            family = FAMILIES[split][(idx + ai) % len(FAMILIES[split])]
            rendered = render_state(state, split=split, family=family, rng=rng)
            oracle = evaluate(state, spec=spec)
            rows.append(
                {
                    "id": f"v6-{split}-{action.lower()}-{idx:04d}",
                    "split": split,
                    "semantic_family": family,
                    "latent_state": state,
                    "observation": rendered.observation,
                    "factor_evidence_map": rendered.factor_evidence_map,
                    "oracle_action": oracle.action,
                    "oracle_rule": oracle.matched_rule,
                }
            )
    rng.shuffle(rows)
    if len(rows) != count:
        raise AssertionError((split, len(rows), count))
    return rows


def _find_counterfactual_pair(
    *,
    spec: Mapping[str, Any],
    states: Iterable[dict[str, Any]],
    field: str,
    before: Any,
    after: Any,
    rng: random.Random,
) -> tuple[dict[str, Any], dict[str, Any]]:
    candidates = [dict(s) for s in states if s[field] == before]
    rng.shuffle(candidates)
    fallback: tuple[dict[str, Any], dict[str, Any]] | None = None
    for left in candidates:
        right = dict(left)
        right[field] = after
        if not validate_state(spec, right).valid:
            continue
        lo = evaluate(left, spec=spec)
        ro = evaluate(right, spec=spec)
        if lo.status != "VALID_DECISION" or ro.status != "VALID_DECISION":
            continue
        if fallback is None:
            fallback = (left, right)
        if lo.action != ro.action:
            return left, right
    if fallback is not None:
        return fallback
    raise RuntimeError(f"unable to construct counterfactual transition {field}:{before}->{after}")


def _counterfactual_rows(spec: Mapping[str, Any], pools: Mapping[str, list[dict[str, Any]]], rng: random.Random) -> list[dict[str, Any]]:
    all_states = [state for pool in pools.values() for state in pool]
    rows: list[dict[str, Any]] = []
    for pair_idx in range(PAIR_SIZES["counterfactual"]):
        field, before, after = TRANSITIONS[pair_idx % len(TRANSITIONS)]
        left, right = _find_counterfactual_pair(spec=spec, states=all_states, field=field, before=before, after=after, rng=rng)
        family = "reported_speech" if pair_idx % 2 else "direct_declarative"
        left_rendered = render_state(left, split="development_ood", family=family, rng=rng)
        right_rendered = render_state(right, split="development_ood", family=family, rng=rng)
        lo = evaluate(left, spec=spec)
        ro = evaluate(right, spec=spec)
        pair_id = f"v6-counterfactual-{pair_idx:04d}"
        for member, state, rendered, oracle in (("a", left, left_rendered, lo), ("b", right, right_rendered, ro)):
            rows.append(
                {
                    "id": f"{pair_id}-{member}",
                    "pair_id": pair_id,
                    "pair_member": member,
                    "transition_field": field,
                    "transition_from": before,
                    "transition_to": after,
                    "split": "counterfactual",
                    "semantic_family": family,
                    "latent_state": state,
                    "observation": rendered.observation,
                    "factor_evidence_map": rendered.factor_evidence_map,
                    "oracle_action": oracle.action,
                    "oracle_rule": oracle.matched_rule,
                }
            )
    return rows


def _invariance_rows(spec: Mapping[str, Any], pools: Mapping[str, list[dict[str, Any]]], rng: random.Random) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    families = [
        ("direct_declarative", "conversational_dialogue"),
        ("direct_declarative", "implication"),
        ("direct_declarative", "passive_voice"),
        ("compact_notes", "long_form_narrative"),
        ("direct_declarative", "reported_speech"),
        ("email_issue_tracker", "contrast_clauses"),
    ]
    for pair_idx in range(PAIR_SIZES["invariance"]):
        action = ACTIONS[pair_idx % len(ACTIONS)]
        state = dict(pools[action][rng.randrange(len(pools[action]))])
        fa, fb = families[pair_idx % len(families)]
        ra = render_state(state, split="validation", family=fa, rng=rng)
        rb = render_state(state, split="rendering_holdout", family=fb, rng=rng)
        oracle = evaluate(state, spec=spec)
        pair_id = f"v6-invariance-{pair_idx:04d}"
        for member, family, rendered in (("a", fa, ra), ("b", fb, rb)):
            rows.append(
                {
                    "id": f"{pair_id}-{member}",
                    "pair_id": pair_id,
                    "pair_member": member,
                    "split": "invariance",
                    "semantic_family": family,
                    "latent_state": state,
                    "observation": rendered.observation,
                    "factor_evidence_map": rendered.factor_evidence_map,
                    "oracle_action": oracle.action,
                    "oracle_rule": oracle.matched_rule,
                }
            )
    return rows


def _jsonl_bytes(rows: list[dict[str, Any]]) -> bytes:
    return ("".join(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n" for row in rows)).encode("utf-8")


def generate(out_dir: Path, *, seed: int = SEED) -> dict[str, Any]:
    rng = random.Random(seed)
    spec = load_spec()
    pools = _state_pools(spec)
    out_dir.mkdir(parents=True, exist_ok=True)

    split_rows: dict[str, list[dict[str, Any]]] = {}
    for split, count in SPLIT_SIZES.items():
        split_rows[split] = _balanced_rows(split=split, count=count, pools=pools, spec=spec, rng=rng)
    split_rows["counterfactual"] = _counterfactual_rows(spec, pools, rng)
    split_rows["invariance"] = _invariance_rows(spec, pools, rng)

    hashes: dict[str, str] = {}
    counts: dict[str, int] = {}
    action_counts: dict[str, dict[str, int]] = {}
    observations_seen: dict[str, str] = {}
    for split, rows in split_rows.items():
        data = _jsonl_bytes(rows)
        path = out_dir / f"{split}.jsonl"
        path.write_bytes(data)
        hashes[path.name] = hashlib.sha256(data).hexdigest()
        counts[split] = len(rows)
        distribution: dict[str, int] = defaultdict(int)
        for row in rows:
            distribution[str(row["oracle_action"])] += 1
            obs_hash = hashlib.sha256(row["observation"].encode("utf-8")).hexdigest()
            if obs_hash in observations_seen:
                raise RuntimeError(f"duplicate rendered observation across dataset: {row['id']} and {observations_seen[obs_hash]}")
            observations_seen[obs_hash] = row["id"]
        action_counts[split] = dict(sorted(distribution.items()))

    manifest = {
        "schema_version": 1,
        "candidate": "Candidate-v6",
        "seed": seed,
        "source_commit": os.environ.get("CANDIDATE_V6_SOURCE_COMMIT", "UNSET"),
        "spec_sha256": spec_sha256(),
        "counts": counts,
        "action_counts": action_counts,
        "sha256": hashes,
        "families": FAMILIES,
        "lexical_partition": {
            "train_validation": "BASE",
            "lexical_holdout": "LEXICAL_HOLDOUT",
        },
        "candidate_v3_protected_access": 0,
        "candidate_v4_protected_access": 0,
        "candidate_v5_holdout_reuse": False,
    }
    manifest_bytes = (json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    (out_dir / "manifest.json").write_bytes(manifest_bytes)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="data/candidate_v6_development")
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    manifest = generate(Path(args.out), seed=args.seed)
    print(json.dumps(manifest, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
