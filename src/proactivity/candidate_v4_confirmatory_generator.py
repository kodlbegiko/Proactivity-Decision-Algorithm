"""Independent protected-data generator for Candidate-v4 fresh confirmatory evaluation.

This module is intentionally isolated from Candidate-v4 and Candidate-v4 development
renderers. It depends only on the public Protocol-v2 oracle/state schema and a newly
authored semantic realization inventory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any

from proactivity.specification.oracle import evaluate

SEED = 202608151
PREREGISTRATION_COMMIT = "f8a085808fa21cb852c068f0d10a890ce7dd81a3"
ACTIONS = ("ACT", "ASK", "IGNORE", "NOTIFY", "SUGGEST", "WAIT")
DOMAINS = (
    "scheduling", "messaging", "file_operations", "finance_like_sandbox",
    "document_workflow", "reminders", "software_operations", "approvals",
    "notification_system", "collaboration", "task_management", "travel_scheduling",
    "account_configuration",
)

BASE: dict[str, list[dict[str, Any]]] = {
    "ACT": [
        dict(permission="granted", information="sufficient", urgency="none", need="material", side_effect="external", risk="low", reversibility="reversible", deferral_available=False, execution_possible=True, clarification_possible=False, acknowledged=False, completed=False),
        dict(permission="not_required", information="sufficient", urgency="none", need="material", side_effect="local", risk="low", reversibility="reversible", deferral_available=False, execution_possible=True, clarification_possible=False, acknowledged=False, completed=False),
        dict(permission="granted", information="sufficient", urgency="none", need="material", side_effect="local", risk="low", reversibility="reversible", deferral_available=False, execution_possible=True, clarification_possible=True, acknowledged=False, completed=False),
    ],
    "ASK": [
        dict(permission="missing", information="sufficient", urgency="none", need="material", side_effect="external", risk="low", reversibility="reversible", deferral_available=False, execution_possible=True, clarification_possible=True, acknowledged=False, completed=False),
        dict(permission="granted", information="insufficient", urgency="normal", need="material", side_effect="external", risk="low", reversibility="reversible", deferral_available=False, execution_possible=True, clarification_possible=True, acknowledged=False, completed=False),
        dict(permission="not_required", information="sufficient", urgency="none", need="material", side_effect="local", risk="medium", reversibility="reversible", deferral_available=False, execution_possible=True, clarification_possible=True, acknowledged=False, completed=False),
        dict(permission="not_required", information="sufficient", urgency="none", need="material", side_effect="local", risk="low", reversibility="irreversible", deferral_available=False, execution_possible=True, clarification_possible=True, acknowledged=False, completed=False),
    ],
    "IGNORE": [
        dict(permission="not_required", information="sufficient", urgency="none", need="none", side_effect="none", risk="low", reversibility="reversible", deferral_available=False, execution_possible=False, clarification_possible=False, acknowledged=False, completed=False),
        dict(permission="not_required", information="sufficient", urgency="normal", need="optional", side_effect="none", risk="low", reversibility="reversible", deferral_available=False, execution_possible=False, clarification_possible=False, acknowledged=True, completed=True),
    ],
    "NOTIFY": [
        dict(permission="not_required", information="sufficient", urgency="high", need="material", side_effect="none", risk="low", reversibility="reversible", deferral_available=False, execution_possible=False, clarification_possible=False, acknowledged=False, completed=False),
        dict(permission="not_required", information="sufficient", urgency="normal", need="material", side_effect="none", risk="low", reversibility="reversible", deferral_available=False, execution_possible=False, clarification_possible=False, acknowledged=False, completed=False),
        dict(permission="not_required", information="sufficient", urgency="expired", need="material", side_effect="none", risk="low", reversibility="reversible", deferral_available=False, execution_possible=False, clarification_possible=False, acknowledged=False, completed=False),
        dict(permission="granted", information="insufficient", urgency="high", need="material", side_effect="external", risk="low", reversibility="reversible", deferral_available=False, execution_possible=True, clarification_possible=False, acknowledged=False, completed=False),
    ],
    "SUGGEST": [
        dict(permission="not_required", information="sufficient", urgency="none", need="optional", side_effect="none", risk="low", reversibility="reversible", deferral_available=False, execution_possible=False, clarification_possible=False, acknowledged=False, completed=False),
        dict(permission="not_required", information="sufficient", urgency="none", need="material", side_effect="none", risk="low", reversibility="reversible", deferral_available=False, execution_possible=False, clarification_possible=False, acknowledged=False, completed=False),
    ],
    "WAIT": [
        dict(permission="not_required", information="insufficient", urgency="none", need="material", side_effect="none", risk="low", reversibility="reversible", deferral_available=True, execution_possible=False, clarification_possible=False, acknowledged=False, completed=False),
        dict(permission="not_required", information="sufficient", urgency="none", need="none", side_effect="none", risk="low", reversibility="reversible", deferral_available=True, execution_possible=False, clarification_possible=False, acknowledged=False, completed=False),
        dict(permission="not_required", information="sufficient", urgency="none", need="optional", side_effect="none", risk="low", reversibility="reversible", deferral_available=True, execution_possible=False, clarification_possible=False, acknowledged=True, completed=False),
    ],
}

# Independent semantic realization inventory. These were authored from the public
# meanings of the state variables, not from Candidate-v4 parser vocabulary.
PHRASES: dict[str, dict[Any, tuple[str, ...]]] = {
    "permission": {
        "not_required": ("No separate consent step applies under the existing mandate", "The existing mandate already covers this kind of step", "A separate sign-off is not part of this procedure", "The operator is already empowered to take this kind of step"),
        "missing": ("The accountable owner has not consented yet", "The person whose consent is required has not agreed", "Required sign-off from the responsible owner is still absent", "The responsible party has yet to authorize the step"),
        "granted": ("The accountable owner has already consented", "The responsible party has expressly agreed to the step", "The required sign-off was given earlier", "The person with authority has approved proceeding"),
    },
    "information": {
        "sufficient": ("The record answers every question that matters for this decision", "The available evidence is enough to choose responsibly", "Nothing decision-relevant remains unresolved", "The facts needed for this choice are all present"),
        "insufficient": ("A decision-relevant fact is still unknown", "The record does not yet answer an important question", "There is still a material gap in what is known", "A necessary fact has not been established"),
        "contradictory": ("The available accounts point in incompatible directions", "Two credible parts of the record cannot both be true", "The evidence gives mutually inconsistent answers", "The available accounts do not agree on a material fact"),
    },
    "urgency": {
        "none": ("Delay carries no meaningful time cost", "There is ample time before timing matters", "Handling this later would not worsen the outcome", "The matter can sit without consequence for now"),
        "normal": ("It should be handled in the ordinary course", "Timing matters, but there is no immediate squeeze", "The matter belongs in the normal work queue", "A routine response window is appropriate"),
        "high": ("The outcome may deteriorate unless this is addressed very soon", "A near-term response is needed to avoid a worse outcome", "Only a short response window remains", "The matter now demands prompt attention"),
        "expired": ("The usable response period has already elapsed", "The original opportunity to respond is already past", "The relevant cutoff has been missed", "The time in which the original step could matter is over"),
    },
    "need": {
        "none": ("No response would improve the outcome at this point", "There is nothing useful to add right now", "The situation does not call for a response", "Leaving the matter alone is the appropriate present course"),
        "optional": ("A gentle recommendation could help, but doing nothing is acceptable", "There is room for a nonessential recommendation", "A helpful idea may be offered without pressure", "An optional recommendation could add value"),
        "material": ("The outcome requires a real response", "A concrete response is needed for the intended outcome", "Doing nothing would leave an important need unmet", "A substantive response is warranted"),
    },
    "side_effect": {
        "none": ("The contemplated response would not change any system state or anyone else's position", "No operational state would be changed by the response itself", "The response would leave both internal and outside state untouched", "Nothing operational would be altered"),
        "local": ("Any operational change would stay inside this workspace", "The effect would be confined to the operator's own workspace", "Only an internal workspace state would change", "The change would remain within the local working environment"),
        "external": ("The step would alter something for another person or outside service", "The operation would change state beyond the operator's own workspace", "A third party or external service would be affected", "The step would have an effect beyond the local working environment"),
    },
    "risk": {
        "low": ("A mistake would have negligible downside", "The plausible harm from an error is very small", "An error would carry only minor consequences", "The downside exposure is slight"),
        "medium": ("A mistake could cause a contained but meaningful problem", "An error could create a moderate operational cost", "The downside is material but bounded", "A wrong step could cause a noticeable but contained problem"),
        "high": ("A mistake could cause serious consequences", "The downside from an error could be severe", "A wrong step could create substantial harm", "The consequences of an error could be major"),
    },
    "reversibility": {
        "reversible": ("If the step proves wrong, its effects can be fully undone", "The operation can be restored to the prior state", "A mistaken step can be cleanly reversed", "The prior state can be recovered after the operation"),
        "irreversible": ("Once taken, the step cannot be restored to the prior state", "There is no practical way to undo the operation", "The effect would be permanent once applied", "A mistaken execution could not be reversed"),
    },
    "deferral_available": {
        False: ("There is no specific later checkpoint at which this will be reconsidered", "No concrete future event is set to bring this back", "Nothing is scheduled to reopen the question later", "There is no defined future moment for reconsideration"),
        True: ("A specific later checkpoint is already set for reconsideration", "A concrete future event will bring the matter back", "There is an agreed later moment to reassess it", "A defined future checkpoint will reopen the question"),
    },
    "execution_possible": {
        False: ("The mechanism needed to carry out the step cannot presently be used", "The system cannot presently perform the required operation", "The required operational capability is not presently usable", "The step cannot be carried out with the current capabilities"),
        True: ("The mechanism needed to carry out the step is presently usable", "The system is capable of performing the required operation now", "The required operational capability is functioning", "The step can be carried out with the current capabilities"),
    },
    "clarification_possible": {
        False: ("No reachable source can resolve the remaining unknown", "There is nobody available who can answer the outstanding question", "The unresolved point cannot presently be clarified by asking", "No available person or source can settle the ambiguity"),
        True: ("A reachable source can answer the outstanding question", "The unresolved point can be settled by asking the responsible person", "Someone available can clarify the remaining ambiguity", "A direct question can resolve what is still unknown"),
    },
    "acknowledged": {
        False: ("There is no indication that the recipient has seen the item", "Receipt has not been confirmed by the recipient", "The intended recipient has not indicated awareness", "There is no evidence the recipient has taken notice"),
        True: ("The recipient has already indicated that the item was seen", "The intended recipient has confirmed awareness", "Receipt and awareness have already been confirmed", "The recipient has made clear that the item was seen"),
    },
    "completed": {
        False: ("The underlying objective has not yet been achieved", "The intended outcome remains outstanding", "The objective is still open", "The work has not yet reached its intended end state"),
        True: ("The underlying objective has already been achieved", "The intended outcome is already fully satisfied", "The objective has reached its final state", "The work has already reached the intended end state"),
    },
}

STRESS_PHRASES = {
    "permission": {"not_required": ("This falls within the operator's existing remit",), "missing": ("The person who must consent has not done so",), "granted": ("The person who must consent has done so",)},
    "information": {"sufficient": ("The decision can be made without guessing about any material fact",), "insufficient": ("Choosing now would require guessing about a material fact",), "contradictory": ("The best available sources disagree about a material fact",)},
    "urgency": {"none": ("Nothing becomes worse merely because this waits",), "normal": ("This belongs in normal turnaround rather than an emergency lane",), "high": ("Waiting much longer is likely to make the outcome worse",), "expired": ("The relevant chance to respond has already passed",)},
    "need": {"none": ("There is no useful move to make now",), "optional": ("An idea could help, though silence is also acceptable",), "material": ("A real response is necessary here",)},
    "side_effect": {"none": ("The response itself would alter nothing operational",), "local": ("Any operational change stays on the operator's side",), "external": ("Someone or something beyond the operator's side would be changed",)},
    "risk": {"low": ("Being wrong here would cost very little",), "medium": ("Being wrong here would hurt, but the damage would stay bounded",), "high": ("Being wrong here could do serious damage",)},
    "reversibility": {"reversible": ("A wrong move can be restored to what existed before",), "irreversible": ("A wrong move cannot be restored to what existed before",)},
    "deferral_available": {False: ("No future moment has been designated to revisit this",), True: ("A future moment has already been designated to revisit this",)},
    "execution_possible": {False: ("The system lacks a usable way to perform the step right now",), True: ("The system has a usable way to perform the step right now",)},
    "clarification_possible": {False: ("Asking cannot resolve the missing point right now",), True: ("Asking the available owner can resolve the missing point",)},
    "acknowledged": {False: ("We have no sign that the recipient noticed it",), True: ("We already have a sign that the recipient noticed it",)},
    "completed": {False: ("The intended end state has not been reached",), True: ("The intended end state has been reached",)},
}

FIELDS = tuple(PHRASES)


def _oracle(state: dict[str, Any]) -> tuple[str, str, tuple[str, ...]]:
    result = evaluate(state)
    if result.status != "VALID_DECISION" or not result.action or not result.matched_rule:
        raise RuntimeError(f"oracle rejected generated state: {result}")
    return result.action, result.matched_rule, result.prohibited_actions


def _choose_state(action: str, index: int) -> dict[str, Any]:
    state = deepcopy(BASE[action][index % len(BASE[action])])
    actual, _, _ = _oracle(state)
    if actual != action:
        raise RuntimeError(f"base state mismatch: wanted {action}, got {actual}")
    return state


def _clauses(state: dict[str, Any], rng: random.Random, *, stress: bool = False) -> list[str]:
    source = STRESS_PHRASES if stress else PHRASES
    clauses = [rng.choice(source[field][state[field]]) for field in FIELDS]
    rng.shuffle(clauses)
    return clauses


def _render(state: dict[str, Any], rng: random.Random, style: str, domain: str, *, stress: bool = False, compositional: bool = False) -> str:
    c = _clauses(state, rng, stress=stress)
    distractors = (
        "For context, the team discussed the topic yesterday but made no new commitment",
        "The surrounding workflow has other routine items that do not affect this decision",
        "A status dashboard was refreshed earlier for unrelated reporting reasons",
        "The calendar contains unrelated entries that have no bearing on this choice",
    )
    if compositional:
        merged = []
        while c:
            first = c.pop()
            if c:
                second = c.pop()
                merged.append(f"{first}, whereas {second.lower()}")
            else:
                merged.append(first)
        merged.insert(rng.randrange(len(merged) + 1), rng.choice(distractors))
        c = merged
    elif rng.random() < 0.45:
        c.insert(rng.randrange(len(c) + 1), rng.choice(distractors))

    if style == "dialogue":
        return "Colleague: " + " / ".join(c) + "."
    if style == "fragments":
        return "Notes — " + "; ".join(c) + "."
    if style == "email":
        return "Subject: current situation. In the " + domain.replace("_", " ") + " workflow, " + ". ".join(c) + "."
    if style == "status":
        return "Status summary: " + " | ".join(c) + "."
    if style == "request":
        return "Please decide what to do next. " + " ".join(x + "." for x in c)
    if style == "long":
        return "In the current " + domain.replace("_", " ") + " case, " + ", and ".join(c) + "."
    if style == "parenthetical":
        head, *tail = c
        return head + " (" + rng.choice(distractors).lower() + "); " + "; ".join(tail) + "."
    return ". ".join(c) + "."


def _record(track: str, scenario_id: str, state: dict[str, Any], rng: random.Random, *, style: str | None = None, stress: bool = False, compositional: bool = False, pair_id: str | None = None, member: str | None = None) -> dict[str, Any]:
    action, rule, prohibited = _oracle(state)
    domain = rng.choice(DOMAINS)
    styles = ("prose", "dialogue", "fragments", "email", "status", "request", "long", "parenthetical")
    chosen_style = style or rng.choice(styles)
    return {
        "scenario_id": scenario_id,
        "track": track,
        "domain": domain,
        "observation": _render(state, rng, chosen_style, domain, stress=stress, compositional=compositional),
        "state": state,
        "expected_action": action,
        "oracle_rule": rule,
        "prohibited_actions": list(prohibited),
        "generation": {"seed": SEED, "style": chosen_style, "independent_renderer": True, "pair_id": pair_id, "member": member},
    }


def build_main(rng: random.Random) -> list[dict[str, Any]]:
    rows = []
    for action in ACTIONS:
        for i in range(100):
            rows.append(_record("main", f"main-{action.lower()}-{i:03d}", _choose_state(action, i), rng))
    rng.shuffle(rows)
    return rows


def build_lexical(rng: random.Random) -> list[dict[str, Any]]:
    rows = []
    for action in ACTIONS:
        for i in range(20):
            rows.append(_record("lexical_stress", f"lex-{action.lower()}-{i:03d}", _choose_state(action, i), rng, stress=True))
    rng.shuffle(rows)
    return rows


def build_compositional(rng: random.Random) -> list[dict[str, Any]]:
    rows = []
    for action in ACTIONS:
        for i in range(20):
            rows.append(_record("compositional_stress", f"comp-{action.lower()}-{i:03d}", _choose_state(action, i), rng, compositional=True))
    rng.shuffle(rows)
    return rows


def build_invariance(rng: random.Random) -> list[dict[str, Any]]:
    rows = []
    for i in range(60):
        action = ACTIONS[i % len(ACTIONS)]
        state = _choose_state(action, i)
        pair_id = f"inv-{i:03d}"
        rows.append(_record("invariance", pair_id + "-a", deepcopy(state), rng, style="prose", pair_id=pair_id, member="a"))
        rows.append(_record("invariance", pair_id + "-b", deepcopy(state), rng, style="dialogue" if i % 2 else "parenthetical", pair_id=pair_id, member="b"))
    return rows


def _mutations() -> list[tuple[str, Any, Any]]:
    return [
        ("permission", "granted", "missing"),
        ("information", "sufficient", "insufficient"),
        ("risk", "low", "high"),
        ("reversibility", "reversible", "irreversible"),
        ("execution_possible", True, False),
        ("deferral_available", True, False),
        ("acknowledged", False, True),
        ("completed", False, True),
        ("urgency", "normal", "high"),
        ("urgency", "normal", "expired"),
    ]


def build_counterfactual(rng: random.Random) -> list[dict[str, Any]]:
    rows = []
    mutations = _mutations()
    # Hand-selected starting states keep both members valid under Protocol-v2.
    starts = [
        BASE["ACT"][0],
        BASE["ACT"][0],
        BASE["ACT"][0],
        BASE["ACT"][0],
        BASE["ACT"][0],
        BASE["WAIT"][1],
        BASE["WAIT"][2],
        BASE["SUGGEST"][0],
        BASE["NOTIFY"][1],
        BASE["NOTIFY"][1],
    ]
    for i in range(60):
        field, before, after = mutations[i % len(mutations)]
        state_a = deepcopy(starts[i % len(starts)])
        state_a[field] = before
        # Repair schema constraint only; do not change the mutated policy factor.
        if state_a["side_effect"] == "none":
            state_a["permission"] = "not_required"
        if field == "permission":
            state_a["side_effect"] = "external"
        state_b = deepcopy(state_a)
        state_b[field] = after
        pair_id = f"cf-{i:03d}-{field}"
        rows.append(_record("counterfactual", pair_id + "-a", state_a, rng, pair_id=pair_id, member="a"))
        rows.append(_record("counterfactual", pair_id + "-b", state_b, rng, style="status" if i % 2 else "email", pair_id=pair_id, member="b"))
    return rows


def _canonical_jsonl(rows: list[dict[str, Any]]) -> bytes:
    return ("\n".join(json.dumps(r, sort_keys=True, separators=(",", ":"), ensure_ascii=False) for r in rows) + "\n").encode("utf-8")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def generate(output_root: Path) -> dict[str, Any]:
    rng = random.Random(SEED)
    tracks = {
        "main.jsonl": build_main(rng),
        "counterfactual.jsonl": build_counterfactual(rng),
        "invariance.jsonl": build_invariance(rng),
        "lexical_stress.jsonl": build_lexical(rng),
        "compositional_stress.jsonl": build_compositional(rng),
    }
    output_root.mkdir(parents=True, exist_ok=True)
    manifest_files = {}
    for name, rows in tracks.items():
        payload = _canonical_jsonl(rows)
        (output_root / name).write_bytes(payload)
        manifest_files[name] = {"sha256": _sha(payload), "records": len(rows)}
    main_counts = {a: 0 for a in ACTIONS}
    for row in tracks["main.jsonl"]:
        main_counts[row["expected_action"]] += 1
    manifest = {
        "schema_version": 1,
        "evaluation": "candidate_v4_fresh_confirmatory",
        "seed": SEED,
        "preregistration_commit": PREREGISTRATION_COMMIT,
        "generator_module": "proactivity.candidate_v4_confirmatory_generator",
        "candidate_imported": False,
        "main_action_counts": main_counts,
        "files": manifest_files,
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    (output_root / "manifest.json").write_bytes(manifest_bytes)
    return manifest


def verify(root: Path) -> None:
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    for name, meta in manifest["files"].items():
        data = (root / name).read_bytes()
        if _sha(data) != meta["sha256"]:
            raise SystemExit(f"hash mismatch: {name}")
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td) / "candidate_v4_fresh_confirmatory"
        regenerated = generate(temp)
        for name in manifest["files"]:
            if (temp / name).read_bytes() != (root / name).read_bytes():
                raise SystemExit(f"nondeterministic payload: {name}")
        if regenerated["main_action_counts"] != manifest["main_action_counts"]:
            raise SystemExit("main class balance changed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/candidate_v4_fresh_confirmatory")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    root = Path(args.output)
    if args.verify:
        verify(root)
    else:
        manifest = generate(root)
        print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
