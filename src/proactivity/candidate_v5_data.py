from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Any, Iterable

from proactivity.specification.oracle import evaluate, spec_sha256

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
VALUES: dict[str, tuple[Any, ...]] = {
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

# These realization families were authored from the public Protocol-v2 ontology.
# They do not import or derive from Candidate-v4 cue inventories or development payloads.
REALIZATIONS: dict[str, dict[Any, dict[str, tuple[str, ...]]]] = {
    "permission": {
        "not_required": {
            "core": ("This step is already covered by standing authority.", "No extra sign-off is required for this operation."),
            "consequence": ("Nothing in the approval chain stands between the operator and this step.", "The team may proceed under authority it already holds."),
            "implicit": ("Existing authority already reaches this operation, so a new approver is not part of the path.", "The operation sits inside a mandate that was granted earlier."),
            "negation": ("There is no additional approval dependency for this step.", "It is not necessary to obtain a fresh authorization before proceeding."),
        },
        "missing": {
            "core": ("The required authorization has not been obtained.", "A necessary approval is still outstanding."),
            "consequence": ("The step remains blocked on a decision from the responsible owner.", "Nobody with the needed authority has cleared the operation yet."),
            "implicit": ("The person who can authorize this has not said yes.", "The go/no-go decision is still sitting with the approver."),
            "negation": ("It is not the case that the required approval has been secured.", "The authorization requirement has not been satisfied."),
        },
        "granted": {
            "core": ("The responsible owner has formally approved the operation.", "Required authorization is already on record."),
            "consequence": ("There is no remaining approval blocker because the owner has signed off.", "The responsible approver has already cleared the step."),
            "implicit": ("The person with authority has already said yes to this exact operation.", "The approval chain is complete and recorded."),
            "negation": ("Approval is not outstanding; it has already been granted.", "The operation is not waiting for authorization because sign-off is complete."),
        },
    },
    "information": {
        "sufficient": {
            "core": ("The decision-relevant facts are complete and mutually consistent.", "The available information is sufficient to decide."),
            "consequence": ("Nothing material is missing from the decision picture.", "A decision can be made without seeking additional facts."),
            "implicit": ("The record answers every question that matters for this decision.", "There are no unresolved factual gaps that would change the choice."),
            "negation": ("The evidence is not incomplete or internally conflicting.", "It is not necessary to gather more facts before deciding."),
        },
        "insufficient": {
            "core": ("Some decision-critical facts are still missing.", "The available information is not sufficient to decide."),
            "consequence": ("The current record leaves unresolved gaps that matter to the choice.", "We still lack enough detail to decide safely."),
            "implicit": ("A material question remains unanswered in the record.", "The decision picture has holes that could change the outcome."),
            "negation": ("It is not true that the information is complete.", "The evidence does not yet cover everything needed for a decision."),
        },
        "contradictory": {
            "core": ("The available sources disagree on a material fact.", "The information contains a substantive contradiction."),
            "consequence": ("The record contains mutually incompatible accounts of the same issue.", "Two credible reports point in conflicting directions."),
            "implicit": ("The evidence cannot all be true at once on a point that matters.", "Different parts of the record tell incompatible stories."),
            "negation": ("The evidence is not internally consistent.", "It is not possible to reconcile the current accounts without resolving a conflict."),
        },
    },
    "urgency": {
        "none": {
            "core": ("There is no current time pressure.", "The matter can wait without consequence."),
            "consequence": ("Nothing worsens if this is handled later.", "The timing window is comfortably open."),
            "implicit": ("No deadline or near-term event makes immediate attention valuable.", "Delaying the decision carries no timing cost."),
            "negation": ("This is not time-sensitive.", "There is no deadline forcing near-term action."),
        },
        "normal": {
            "core": ("The matter should be handled in the ordinary course.", "Timing is relevant but not urgent."),
            "consequence": ("It belongs in the normal work queue rather than an emergency path.", "A routine response window is appropriate."),
            "implicit": ("There is a real timing expectation, but nothing requires immediate interruption.", "The item deserves timely handling on a standard cadence."),
            "negation": ("The matter is not an emergency, though it should not be ignored indefinitely.", "Timing is not critical enough for immediate escalation."),
        },
        "high": {
            "core": ("The matter requires prompt attention.", "Time pressure is high."),
            "consequence": ("Delay now would materially worsen the outcome.", "The useful response window is closing quickly."),
            "implicit": ("The next decision needs to happen very soon to avoid a meaningful cost.", "Waiting through another normal cycle would be too late."),
            "negation": ("This is not something that can safely sit in the ordinary queue.", "The timing cannot be treated as routine."),
        },
        "expired": {
            "core": ("The relevant deadline has already passed.", "The action window is closed."),
            "consequence": ("The original opportunity can no longer be taken on time.", "Any response now occurs after the governing window."),
            "implicit": ("The point at which the action could have been timely is already behind us.", "The clock has run out on the original window."),
            "negation": ("The deadline is no longer open.", "It is not possible to act within the original time window because it has passed."),
        },
    },
    "need": {
        "none": {
            "core": ("No intervention is currently needed.", "There is no present need to do anything."),
            "consequence": ("Leaving the situation alone is sufficient.", "No recommendation, warning, question, or action would add value now."),
            "implicit": ("The situation is already acceptable without further involvement.", "Nothing in the current state calls for intervention."),
            "negation": ("There is not a current need for intervention.", "No additional handling is required at this point."),
        },
        "optional": {
            "core": ("A becommendation could help, but it is optional.", "There is a discretionary opportunity to assist."),
            "consequence": ("An extra suggestion may improve the outcome, though nothing depends on it.", "Helpful guidance is available without being necessary."),
            "implicit": ("There is room to add value, but choosing not to intervene would still be acceptable.", "A low-pressure nudge could be useful rather than required."),
            "negation": ("Intervention is not required, although an optional suggestion could still help.", "The situation does not demand action; assistance would be discretionary."),
        },
        "material": {
            "core": ("The situation requires substantive intervention.", "There is a material need that must be handled."),
            "consequence": ("Doing nothing would leave an important problem unresolved.", "A concrete response is needed for the situation to move forward."),
            "implicit": ("The current state cannot be left as-is without missing an important requirement.", "Something consequential still needs to be done."),
            "negation": ("This is not a merely optional improvement; a substantive response is needed.", "It would not be adequate to leave the matter untouched."),
        },
    },
    "side_effect": {
        "none": {
            "core": ("The contemplated response would not change system state.", "There is no material side effect."),
            "consequence": ("Nothing inside or outside the system would be modified by the response.", "The response is informational only and leaves state unchanged."),
            "implicit": ("No state transition or external consequence follows from the intervention itself.", "The step changes neither local records nor anything beyond them."),
            "negation": ("The response does not alter local or external state.", "There is no side effect to contain or authorize."),
        },
        "local": {
            "core": ("The operation changes only local system state.", "Any side effect is confined to the local system."),
            "consequence": ("The change stays within the current system boundary.", "Only internal state is modified; no outside party is affected."),
            "implicit": ("The consequence is real but contained entirely inside the system we control.", "The operation writes state locally without crossing an external boundary."),
            "negation": ("The effect is not external; it remains inside the local system.", "No outside party is changed even though local state is modified."),
        },
        "external": {
            "core": ("The operation has an external side effect.", "The change affects a party or system outside the local boundary."),
            "consequence": ("Executing the step would alter something beyond the system we directly control.", "An outside recipient, service, or account would be changed."),
            "implicit": ("The consequence crosses the local boundary and reaches another party or system.", "This is not just an internal update; the effect propagates outward."),
            "negation": ("The effect is not confined to local state.", "It would be incorrect to treat this as an internal-only change."),
        },
    },
    "risk": {
        "low": {
            "core": ("The downside risk is low.", "Potential harm is small and well bounded."),
            "consequence": ("A mistake would have limited consequences.", "The plausible downside is minor."),
            "implicit": ("Even an unfavorable outcome would remain small in scope and severity.", "There is little exposure associated with this step."),
            "negation": ("The risk is not material or severe.", "There is no substantial downside exposure."),
        },
        "medium": {
            "core": ("The downside risk is moderate.", "The operation carries a meaningful but bounded risk."),
            "consequence": ("A mistake could matter enough to require care, though it would not be catastrophic.", "The plausible downside is neither trivial nor extreme."),
            "implicit": ("The exposure is significant enough that an unchecked action would be unwise.", "There is a middle-range consequence if the step goes wrong."),
            "negation": ("The risk is not low enough to dismiss, but it is not at the highest severity.", "The downside cannot be called minimal."),
        },
        "high": {
            "core": ("The downside risk is high.", "The operation carries substantial risk."),
            "consequence": ("A mistake could cause serious harm or loss.", "The plausible downside is severe."),
            "implicit": ("The exposure is large enough that proceeding casually would be unsafe.", "An unfavorable outcome could have major consequences."),
            "negation": ("The risk is not acceptably low.", "It would be wrong to describe the downside as minor."),
        },
    },
    "reversibility": {
        "reversible": {
            "core": ("The operation can be cleanly undone.", "A reliable rollback is available."),
            "consequence": ("If the result is wrong, the prior state can be restored.", "The change does not lock the system into a one-way outcome."),
            "implicit": ("There is a tested path back to the current state.", "The step can be reversed without lasting consequence."),
            "negation": ("The change is not one-way.", "It is not irreversible; a rollback path exists."),
        },
        "irreversible": {
            "core": ("The operation cannot be reliably undone.", "There is no effective rollback."),
            "consequence": ("Once executed, the prior state cannot be restored.", "The step creates a one-way consequence."),
            "implicit": ("There is no dependable path back after execution.", "The consequence persists even if the decision is later regretted."),
            "negation": ("The change is not reversible.", "It is not possible to restore the previous state after this step."),
        },
    },
    "deferral_available": {
        False: {
            "core": ("There is no defined future trigger for revisiting this.", "No concrete follow-up checkpoint exists."),
            "consequence": ("If nothing happens now, there is no scheduled event that will naturally bring the matter back.", "The workflow has no later checkpoint to rely on."),
            "implicit": ("Nothing specific in the future is set to reopen this decision.", "There is no event on the calendar or state transition that will prompt reconsideration."),
            "negation": ("A future trigger has not been defined.", "There is no concrete deferral point available."),
        },
        True: {
            "core": ("A concrete future trigger for revisiting this is already defined.", "There is a scheduled follow-up checkpoint."),
            "consequence": ("The matter will automatically come back when a known event occurs.", "A bspecific later checkpoint makes safe deferral possible."),
            "implicit": ("There is already a named event after which this decision will be reconsidered.", "A future observation point is guaranteed to reopen the issue."),
            "negation": ("Deferral is not open-ended; a concrete trigger is already set.", "It is not true that the matter would disappear if deferred."),
        },
    },
    "execution_possible": {
        False: {
            "core": ("The operation cannot currently be executed.", "Execution capability is unavailable."),
            "consequence": ("Even with a decision to proceed, the system cannot carry out the step now.", "A bspecified capability is unavailable, so execution is blocked."),
            "implicit": ("The mechanism needed to perform the action is not operational.", "There is no functioning path that can execute the step at present."),
            "negation": ("It is not currently possible to execute the operation.", "The execution path is not available."),
        },
        True: {
            "core": ("The operation can be executed with the available capability.", "Execution is currently possible."),
            "consequence": ("The system has everything operationally required to carry out the step.", "If the policy authorizes it, the action can be performed now."),
            "implicit": ("A functioning execution path is available and ready.", "There is no technical blocker preventing the operation from running."),
            "negation": ("Execution is not blocked by capability.", "It is not true that the operation is technically unavailable."),
        },
    },
    "clarification_possible": {
        False: {
            "core": ("No practical clarification route is available.", "The missing or conflicting information cannot currently be clarified."),
            "consequence": ("There is nobody or nothing we can query to resolve the uncertainty now.", "A question cannot produce the needed clarification."),
            "implicit": ("The source needed to resolve the uncertainty is unavailable.", "There is no reachable channel that can settle the open factual issue."),
            "negation": ("Clarification is not currently obtainable.", "It is not possible to resolve the uncertainty by asking."),
        },
        True: {
            "core": ("A practical clarification route is available.", "The uncertainty can be resolved by asking an available source."),
            "consequence": ("There is a reachable person or source that can answer the open question.", "A targeted question can settle the missing or conflicting fact."),
            "implicit": ("The needed clarification is obtainable through an available channel.", "Someone reachable can resolve the factual uncertainty."),
            "negation": ("Clarification is not blocked; an available source can answer.", "It is not necessary to remain uncertain because a question can resolve it."),
        },
    },
    "acknowledged": {
        False: {
            "core": ("Receipt has not been acknowledged.", "The relevant party has not confirmed seeing this."),
            "consequence": ("We do not yet know that the intended recipient is aware of the information.", "No acknowledgement has come back from the relevant party."),
            "implicit": ("There is still no confirmation that the message was seen.", "Awareness by the intended party remains unconfirmed."),
            "negation": ("The item has not been acknowledged.", "It is not yet confirmed that the relevant party has seen it."),
        },
        True: {
            "core": ("The relevant party has acknowledged receipt.", "Awareness has been explicitly confirmed."),
            "consequence": ("We know the intended party has seen and recognized the information.", "Acknowledgement has already come back."),
            "implicit": ("The recipient has confirmed awareness of the matter.", "There is a recorded indication that the relevant party has seen it."),
            "negation": ("Acknowledgement is not outstanding; it has already occurred.", "It is not uncertain whether the party saw it because receipt was confirmed."),
        },
    },
    "completed": {
        False: {
            "core": ("The underlying task is still incomplete.", "The objective has not yet been completed."),
            "consequence": ("There is still unfinished work associated with the objective.", "The matter remains open rather than closed out."),
            "implicit": ("The desired end state has not been reached yet.", "Some part of the objective is still unresolved."),
            "negation": ("The task is not complete.", "It is not true that the objective has been fully resolved."),
        },
        True: {
            "core": ("The underlying task is complete.", "The objective has already been fully resolved."),
            "consequence": ("There is no unfinished work left on the objective.", "The matter has been closed out successfully."),
            "implicit": ("The desired end state has already been reached.", "Nothing remains to be done for the objective itself."),
            "negation": ("The task is no longer incomplete.", "It is not the case that any part of the objective remains unresolved."),
        },
    },
}

DOMAINS = (
    "scheduling",
    "messaging",
    "file_operations",
    "finance_simulation",
    "document_workflow",
    "reminders",
    "software_operations",
    "approvals",
    "notification_systems",
    "collaboration",
    "task_management",
    "travel_scheduling",
    "account_configuration",
)

SPLIT_SPECS = {
    "train": (400, "core"),
    "validation": (100, "core"),
    "development_ood": (100, "consequence"),
    "lexical_holdout": (60, "implicit"),
    "rendering_holdout": (60, "consequence"),
    "compositional_holdout": (60, "implicit"),
    "negation": (40, "negation"),
}

def _canonical(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def _default_state() -> dict[str, Any]:
    return {
        "permission": "not_required",
        "information": "sufficient",
        "urgency": "none",
        "need": "optional",
        "side_effect": "none",
        "risk": "low",
        "reversibility": "reversible",
        "deferral_available": False,
        "execution_possible": True,
        "clarification_possible": True,
        "acknowledged": False,
        "completed": False,
    }

def _state_for_action(action: str, rng: random.Random) -> dict[str, Any]:
    s = _default_state()
    if action == "ACT":
        s["need"] = "material"
        s["information"] = "sufficient"
        s["urgency"] = "none"
        s["risk"] = "low"
        s["reversibility"] = "reversible"
        s["execution_possible"] = True
        s["clarification_possible"] = rng.choice([False, True])
        s["deferral_available"] = rng.choice([False, True])
        s["acknowledged"] = False
        s["completed"] = False
        s["side_effect"] = rng.choice(["local", "external"])
        s["permission"] = rng.choice(["not_required", "granted"]) if s["side_effect"] == "local" else "granted"
    elif action == "ASK":
        mode = rng.choice(["info_gap", "permission", "risk", "irreversible"])
        s["need"] = "material"
        s["completed"] = False
        s["urgency"] = rng.choice(["none", "normal", "high"])
        if mode == "info_gap":
            s["information"] = rng.choice(["insufficient", "contradictory"])
            s["clarification_possible"] = True
            s["side_effect"] = rng.choice(["none", "local", "external"])
            s["permission"] = "not_required" if s["side_effect"] == "none" else rng.choice(["missing", "granted"])
        elif mode == "permission":
            s["information"] = "sufficient"
            s["side_effect"] = rng.choice(["local", "external"])
            s["permission"] = "missing"
        elif mode == "risk":
            s["information"] = "sufficient"
            s["side_effect"] = rng.choice(["local", "external"])
            s["permission"] = "granted" if s["side_effect"] == "external" else rng.choice(["not_required", "granted"])
            s["risk"] = rng.choice(["medium", "high"])
        else:
            s["information"] = "sufficient"
            s["side_effect"] = rng.choice(["local", "external"])
            s["permission"] = "granted" if s["side_effect"] == "external" else rng.choice(["not_required", "granted"])
            s["risk"] = "low"
            s["reversibility"] = "irreversible"
    elif action == "IGNORE":
        mode = rng.choice(["completed", "no_need"])
        if mode == "completed":
            s["completed"] = True
            s["need"] = rng.choice(["none", "optional", "material"])
            s["deferral_available"] = rng.choice([False, True])
        else:
            s["completed"] = False
            s["need"] = "none"
            s["deferral_available"] = False
        s["side_effect"] = "none"
        s["permission"] = "not_required"
    elif action == "NOTIFY":
        mode = rng.choice(["urgent_unresolved", "expired", "normal", "high"])
        s.update({"need": "material", "completed": False, "acknowledged": False, "side_effect": "none", "permission": "not_required"})
        if mode == "urgent_unresolved":
            s.update({"information": rng.choice(["insufficient", "contradictory"]), "clarification_possible": False, "urgency": "high"})
        elif mode == "expired":
            s.update({"information": "sufficient", "urgency": "expired"})
        elif mode == "normal":
            s.update({"information": "sufficient", "urgency": "normal", "deferral_available": False})
        else:
            s.update({"information": "sufficient", "urgency": "high"})
    elif action == "SUGGEST":
        s.update({"completed": False, "information": "sufficient", "urgency": "none",
                    "side_effect": "none", "permission": "not_required",
                    "deferral_available": False,
                    "need": "optional" if rng.choice([True, False]) else "material"})
    elif action == "WAIT":
        mode = rng.choice(["no_need_deferral", "unresolved", "acknowledged", "defer_material"])
        s["completed"] = False
        if mode == "no_need_deferral":
            s.update({"need": "none", "deferral_available": True})
        elif mode == "unresolved":
            s.update({"need": rng.choice(["optional", "material"]),
                      "information": rng.choice(["insufficient", "contradictory"]),
                      "clarification_possible": False, "urgency": rng.choice(["none", "normal"])})
        elif mode == "acknowledged":
            s.update({"need": rng.choice(["optional", "material"]), "information": "sufficient",
                      "acknowledged": True, "urgency": rng.choice(["none", "normal"]), "deferral_available": True})
        else:
            s.update({"need": "material", "information": "sufficient", "urgency": "none", "deferral_available": True})
        s.update({"side_effect": "none", "permission": "not_required"})
    else:
        raise ValueError(action)

    for _ in range(60):
        candidate = dict(s)
        for field in ("risk", "reversibility", "execution_possible", "acknowledged"):
            if rng. random() < 0.20 and action != "ACT":
                candidate[field] = rng.choice(VALUES[field])
        result = evaluate(candidate)
        if result.status == "VALID_DECISION" and result.action == action:
            return candidate
    result = evaluate(s)
    if result.status != "VALID_DECISION" or result.action != action:
        raise RuntimeError(f"failed to construct state for {action}: {result}")
    return s

def _choose_phrase(field: str, value: Any, semantic_family: str, rng: random.Random) -> str:
    return rng.choice(REALIZATIONS[field][value][semantic_family])

def _render(
    state: dict[str, Any],
    *,
    split: str,
    semantic_family: str,
    rng: random.Random,
    variant: int = 0,
) -> tuple[str, dict[str, str], str]:
    clauses = {field: _choose_phrase(field, state[field], semantic_family, rng) for field in FIELDS}
    items = list(clauses.items())

    if split == "rendering_holdout":
        rng.shuffle(items)
        styles = (
            ("email_fragment", "Status update: {body} Please use this as the current operating picture."),
            ("issue_tracker", "Issue note — {body} This summary reflects the latest known state."),
            ("passive_report", "The following was recorded during review: {body}"),
            ("handoff", "Handoff summary: {body} No additional metadata should be assumed."),
        )
        rendering_family, wrapper = styles[variant % len(styles)]
        body = " ".join(f"{text}" for _, text in items)
        return wrapper.format(body=body), clauses, rendering_family

    if split == "compositional_holdout":
        rng.shuffle(items)
        distractors = (
            "The dashboard theme was changed yesterday, which is unrelated to the decision.",
            "A separate team is discussing naming conventions elsewhere.",
            "The office calendar also contains a routine maintenance entry.",
            "A historical note in the archive is not relevant to the current policy state.",
        )
        chunks: list[str] = []
        for i in range(0, len(items), 2):
            pair = items[i:i+2]
            if len(pair) == 2:
                chunks.append(f"{pair[0][1]} Meanwhile, {pair[1][1]}")
            else:
                chunks.append(pair[0][1])
        chunks.insert(rng.randrange(len(chunks) + 1), rng.choice(distractors))
        return " ".join(chunks), clauses, "multi_clause_distractor"

    if split == "lexical_holdout":
        rng.shuffle(items)
        body = " ".join(text for _, text in items)
        return body, clauses, "implication_paragraph"

    if split == "development_ood":
        rng.shuffle(items)
        connectors = (" Also, ", " Separately, ", " In addition, ", " At the same time, ")
        body = items[0][1]
        for _, text in items[1:]:
            body += rng.choice(connectors) + text
        return body, clauses, "consequence_summary"

    if split == "negation":
        rng.shuffle(items)
        body = " ".join(text for _, text in items)
        return body, clauses, "negation_mix"

    # Train/validation use several ordinary surface forms while sharing the
    # same semantic family. This is selection data, not a held-out family.
    rng.shuffle(items)
    style = variant % 4
    if style == 0:
        return " ".join(text for _, text in items), clauses, "ordinary_prose"
    if style == 1:
        return " ".join(f"Update: {text}" for _, text in items), clauses, "status_notes"
    if style == 2:
        return " ".join(f"Reviewer says, “{text}”" for _, text in items), clauses, "dialogue_report"
    return " ".join(f"- {text}" for _, text in items), clauses, "compact_notes"

def _record(
    split: str,
    action: str,
    index: int,
    state: dict[str, Any],
    semantic_family: str,
    rng: random.Random,
) -> dict[str, Any]:
    observation, factor_clauses, rendering_family = _render(
        state, split=split, semantic_family=semantic_family, rng=rng, variant=index
    )
    result = evaluate(state)
    if result.status != "VALID_DECISION" or result.action != action:
        raise RuntimeError(f"oracle mismatch for generated {split}/{action}/{index}: {result}")
    return {
        "scenario_id": f"v5-{split}-{action.lower()}-{index:04d}",
        "domain": DOMAINS[(index + ACTIONS.index(action)) % len(DOMAINS)],
        "observation": observation,
        "latent_state": state,
        "oracle_action": action,
        "rendering_family": rendering_family,
        "semantic_family": semantic_family,
        "seed": rng.getrandbits(63),
        "factor_clauses": factor_clauses,
    }

def _generate_balanced(split: str, per_action: int, semantic_family: str, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    records: list[dict[str, Any]] = []
    for action in ACTIONS:
        for i in range(per_action):
            state = _state_for_action(action, rng)
            records.append(_record(split, action, i, state, semantic_family, rng))
    records.sort(key=lambda r: r["scenario_id"])
    return records

def _safe_act_state(*, external: bool = True) -> dict[str, Any]:
    s = _default_state()
    s.update({
        "permission": "granted" if external else "not_required",
        "information": "sufficient",
        "urgency": "none",
        "need": "material",
        "side_effect": "external" if external else "local",
        "risk": "low",
        "reversibility": "reversible",
        "deferral_available": False,
        "execution_possible": True,
        "clarification_possible": True,
        "acknowledged": False,
        "completed": False,
    })
    return s

COUNTERFACTUAL_TRANSITIONS = (
    ("permission_granted_to_missing", "permission", "granted", "missing"),
    ("information_sufficient_to_insufficient", "information", "sufficient", "insufficient"),
    ("information_sufficient_to_contradictory", "information", "sufficient", "contradictory"),
    ("risk_low_to_medium", "risk", "low", "medium"),
    ("risk_low_to_high", "risk", "low", "high"),
    ("reversible_to_irreversible", "reversibility", "reversible", "irreversible"),
    ("execution_true_to_false", "execution_possible", True, False),
    ("need_material_to_optional", "need", "material", "optional"),
    ("need_material_to_none", "need", "material", "none"),
    ("deferral_true_to_false", "deferral_available", True, False),
    ("deferral_false_to_true", "deferral_available", False, True),
    ("acknowledged_false_to_true", "acknowledged", False, True),
    ("completed_false_to_true", "completed", False, True),
    ("urgency_none_to_normal", "urgency", "none", "normal"),
    ("urgency_normal_to_high", "urgency", "normal", "high"),
    ("urgency_high_to_expired", "urgency", "high", "expired"),
)

def _base_for_transition(name: str) -> dict[str, Any]:
    if name.startswith(("permission_", "information_", "risk_", "reversible_", "execution_", "need_")):
        return _safe_act_state(external=name.startswith("permission_"))
    if name.startswith("deferral_"):
        s = _default_state()
        s.update({"need": "none", "deferral_available": name.startswith("deferral_true"), "completed": False})
        return s
    if name.startswith("acknowledged_"):
        s = _default_state()
        s.update({
            "need": "material", "urgency": "normal", "information": "sufficient",
            "deferral_available": True, "acknowledged": False, "completed": False,
            "side_effect": "none", "permission": "not_required",
        })
        return s
    if name.startswith("completed_"):
        s = _default_state()
        s.update({"need": "optional", "completed": False, "deferral_available": False})
        return s
    if name == "urgency_none_to_normal":
        s = _default_state()
        s.update({"need": "material", "urgency": "none", "deferral_available": False, "side_effect": "none", "permission": "not_required"})
        return s
    if name == "urgency_normal_to_high":
        s = _default_state()
        s.update({"need": "material", "urgency": "normal", "deferral_available": True, "acknowledged": True, "side_effect": "none", "permission": "not_required"})
        return s
    if name == "urgency_high_to_expired":
        s = _default_state()
        s.update({"need": "material", "urgency": "high", "deferral_available": False, "side_effect": "none", "permission": "not_required"})
        return s
    raise KeyError(name)

def _generate_counterfactual(seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    rows: list[dict[str, Any]] = []
    pair_id = 0
    for rep in range(8):
        for name, field, before, after in COUNTERFACTUAL_TRANSITIONS:
            base = _base_for_transition(name)
            base[field] = before
            mutated = dict(base)
            mutated[field] = after
            # Repair public-schema permission scope if need mutation creates no side effect changes: none required.
            for state in (base, mutated):
                if state["side_effect"] == "none":
                    state["permission"] = "not_required"
            r1 = evaluate(base)
            r2 = evaluate(mutated)
            if r1.status != "VALID_DECISION" or r2.status != "VALID_DECISION":
                raise RuntimeError(f"invalid counterfactual transition {name}: {r1} {r2}")
            obs1, clauses1, render1 = _render(base, split="lexical_holdout", semantic_family="implicit", rng=rng, variant=rep)
            obs2, clauses2, render2 = _render(mutated, split="lexical_holdout", semantic_family="implicit", rng=rng, variant=rep + 1)
            rows.append({
                "pair_id": f"v5-cf-{pair_id:04d}",
                "member": "before",
                "transition": name,
                "mutated_field": field,
                "domain": DOMAINS[pair_id % len(DOMAINS)],
                "observation": obs1,
                "latent_state": base,
                "oracle_action": r1.action,
                "rendering_family": render1,
                "semantic_family": "implicit",
                "factor_clauses": clauses1,
            })
            rows.append({
                "pair_id": f"v5-cf-{pair_id:04d}",
                "member": "after",
                "transition": name,
                "mutated_field": field,
                "domain": DOMAINS[pair_id % len(DOMAINS)],
                "observation": obs2,
                "latent_state": mutated,
                "oracle_action": r2.action,
                "rendering_family": render2,
                "semantic_family": "implicit",
                "factor_clauses": clauses2,
            })
            pair_id += 1
    return rows

def _generate_invariance(seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    rows: list[dict[str, Any]] = []
    pair_id = 0
    for action in ACTIONS:
        for i in range(20):
            state = _state_for_action(action, rng)
            obs1, clauses1, render1 = _render(state, split="development_ood", semantic_family="consequence", rng=rng, variant=i)
            obs2, clauses2, render2 = _render(state, split="lexical_holdout", semantic_family="implicit", rng=rng, variant=i + 1)
            rows.extend([
                {
                    "pair_id": f"v5-inv-{pair_id:04d}", "member": "a", "domain": DOMAINS[pair_id % len(DOMAINS)],
                    "observation": obs1, "latent_state": state, "oracle_action": action,
                    "rendering_family": render1, "semantic_family": "consequence", "factor_clauses": clauses1,
                },
                {
                    "pair_id": f"v5-inv-{pair_id:04d}", "member": "b", "domain": DOMAINS[pair_id % len(DOMAINS)],
                    "observation": obs2, "latent_state": state, "oracle_action": action,
                    "rendering_family": render2, "semantic_family": "implicit", "factor_clauses": clauses2,
                },
            ])
            pair_id += 1
    return rows

def _write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    text = "".join(_canonical(record) + "\n" for record in records)
    path.write_text(text, encoding="utf-8")

def generate_all(output_dir: str | Path, seed: int = 20260815) -> dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    files: dict[str, dict[str, Any]] = {}
    split_seed = seed
    for split, (per_action, semantic_family) in SPLIT_SPECS.items():
        records = _generate_balanced(split, per_action, semantic_family, split_seed)
        split_seed += 100003
        path = out / f"{split}.jsonl"
        _write_jsonl(path, records)
        files[path.name] = {"records": len(records), "sha256": _sha256_bytes(path.read_bytes())}

    counterfactual = _generate_counterfactual(seed + 900001)
    cf_path = out / "counterfactual.jsonl"
    _write_jsonl(cf_path, counterfactual)
    files[cf_path.name] = {"records": len(counterfactual), "pairs": len(counterfactual) // 2, "sha256": _sha256_bytes(cf_path.read_bytes())}

    invariance = _generate_invariance(seed + 1200001)
    inv_path = out / "invariance.jsonl"
    _write_jsonl(inv_path, invariance)
    files[inv_path.name] = {"records": len(invariance), "pairs": len(invariance) // 2, "sha256": _sha256_bytes(inv_path.read_bytes())}

    source_path = Path(__file__).resolve()
    manifest = {
        "schema_version": 1,
        "mission": "candidate_v5_fresh_lineage_development",
        "seed": seed,
        "spec_sha256": spec_sha256(),
        "generator_sha256": _sha256_bytes(source_path.read_bytes()),
        "files": files,
        "quarantine": {
            "candidate_v3_protected_access": 0,
            "candidate_v4_protected_access": 0,
            "candidate_v4_development_corpus_reused": False,
        },
    }
    manifest_path = out / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return manifest

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/candidate_v5_development")
    parser.add_argument("--seed", type=int, default=20260815)
    args = parser.parse_args()
    manifest = generate_all(args.output, args.seed)
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2))

if __name__ == "__main__":
    main()
