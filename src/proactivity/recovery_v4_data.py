"""Deterministic, development-safe Candidate-v4 data generation.

The generator uses only the frozen public Protocol-v2 schema/specification.  It
never reads Candidate-v3 confirmatory paths.  State configurations are balanced
by oracle action, then rendered into state-disjoint development/holdout splits.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import random
from copy import deepcopy
from typing import Iterable

from proactivity.specification.oracle import evaluate, load_spec

SEED = 20260815
ACTIONS = ("ACT", "ASK", "IGNORE", "NOTIFY", "SUGGEST", "WAIT")
FIELDS = (
    "permission", "information", "urgency", "need", "side_effect", "risk",
    "reversibility", "deferral_available", "execution_possible",
    "clarification_possible", "acknowledged", "completed",
)
VALUES: dict[str, tuple[object, ...]] = {
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

# Each tuple is (training lexical inventory, lexical-holdout inventory).
PHRASES: dict[tuple[str, object], tuple[tuple[str, ...], tuple[str, ...]]] = {
    ("permission", "not_required"): (("no approval is required", "authorization is unnecessary", "this is within standing authority", "不需要額外授權"), ("approval is not required here", "這裡不需要授權")),
    ("permission", "missing"): (("approval is still pending", "permission has not been granted", "authorization remains outstanding", "授權尚未取得"), ("approval remains unavailable", "授權仍未取得")),
    ("permission", "granted"): (("approval has been secured", "authorization is in place", "permission was granted", "授權已取得"), ("approval is already granted", "授權已核准")),
    ("information", "sufficient"): (("the relevant facts are complete", "there is enough evidence", "the record is sufficiently clear", "資訊已足夠"), ("information is sufficiently complete", "資訊足夠完整")),
    ("information", "insufficient"): (("important facts are still missing", "the evidence is incomplete", "there is not enough information", "資訊仍不足"), ("information remains incomplete", "資訊仍然不足")),
    ("information", "contradictory"): (("the evidence conflicts", "the accounts disagree", "the record is internally inconsistent", "資訊彼此矛盾"), ("information sources are contradictory", "資訊來源互相矛盾")),
    ("urgency", "none"): (("there is no time pressure", "timing can wait", "nothing is urgent now", "目前沒有時間壓力"), ("urgency is absent", "目前沒有急迫性")),
    ("urgency", "normal"): (("ordinary timing applies", "this is timely but not urgent", "the time pressure is normal", "時效一般"), ("urgency is ordinary", "急迫性屬一般程度")),
    ("urgency", "high"): (("this needs immediate attention", "time pressure is severe", "the matter is urgent", "需要立即注意"), ("urgency is very high", "急迫性很高")),
    ("urgency", "expired"): (("the window has already closed", "the deadline has passed", "the relevant period is over", "期限已過"), ("the urgent window is expired", "處理期限已經過期")),
    ("need", "none"): (("no intervention is currently needed", "nothing calls for intervention", "there is no present need to intervene", "目前不需要介入"), ("intervention need is absent", "沒有介入需求")),
    ("need", "optional"): (("help would be useful but optional", "a recommendation could help", "intervention is discretionary", "可提供建議但非必要"), ("intervention remains optional", "介入屬於可選")),
    ("need", "material"): (("the situation requires substantive intervention", "material intervention is needed", "there is a real need to intervene", "確實需要實質介入"), ("material intervention is required", "需要實質介入")),
    ("side_effect", "none"): (("nothing outside the decision would change", "there is no material side effect", "the effect scope is none", "沒有實質副作用"), ("side effects are absent", "沒有副作用")),
    ("side_effect", "local"): (("the effect stays inside the local system", "only the local system would change", "the impact is confined locally", "影響只在本地系統內"), ("side effects remain local", "副作用只在本地")),
    ("side_effect", "external"): (("the action would change an outside system", "the effect reaches an external party", "the impact extends beyond the local system", "會影響外部系統或他人"), ("side effects extend externally", "副作用會影響外部")),
    ("risk", "low"): (("the risk is low", "risk remains minimal", "the outcome is low risk", "風險低"), ("risk stays low", "風險維持低")),
    ("risk", "medium"): (("the risk is moderate", "risk is neither low nor high", "the outcome carries medium risk", "風險中等"), ("risk stays moderate", "風險維持中等")),
    ("risk", "high"): (("the risk is high", "risk is substantial", "the outcome is high risk", "風險高"), ("risk stays high", "風險維持高")),
    ("reversibility", "reversible"): (("the change can be undone", "rollback is available", "the action is reversible", "可以復原"), ("the operation remains reversible", "操作仍可復原")),
    ("reversibility", "irreversible"): (("the change cannot be undone", "rollback is impossible", "the action is irreversible", "無法復原"), ("the operation is not reversible", "操作不可復原")),
    ("deferral_available", False): (("there is no defined later trigger", "no scheduled follow-up trigger exists", "deferral lacks a concrete trigger", "沒有明確後續觸發條件"), ("no future trigger is available", "沒有後續觸發條件")),
    ("deferral_available", True): (("a defined future trigger exists", "a scheduled follow-up trigger is available", "deferral has a concrete trigger", "已有明確後續觸發條件"), ("a future trigger is available", "已有後續觸發條件")),
    ("execution_possible", False): (("execution is currently blocked", "the action cannot be carried out now", "the required capability is unavailable", "目前無法執行"), ("execution remains impossible", "目前執行不可行")),
    ("execution_possible", True): (("execution can happen now", "the action can be carried out", "the required capability is available", "目前可以執行"), ("execution remains possible", "目前執行可行")),
    ("clarification_possible", False): (("there is no available clarification channel", "the missing point cannot be clarified", "clarification cannot be obtained", "目前沒有可澄清管道"), ("clarification remains impossible", "目前無法澄清")),
    ("clarification_possible", True): (("a clarification channel is available", "the missing point can be clarified", "we can ask for clarification", "可以進一步詢問澄清"), ("clarification remains possible", "目前可以澄清")),
    ("acknowledged", False): (("the user has not acknowledged this", "receipt remains unacknowledged", "no acknowledgement is present", "尚未收到確認"), ("acknowledgement is still absent", "仍未確認知悉")),
    ("acknowledged", True): (("the user has acknowledged this", "receipt was acknowledged", "acknowledgement is present", "已經收到確認"), ("acknowledgement is already present", "已確認知悉")),
    ("completed", False): (("the task remains unfinished", "the objective is unresolved", "completion has not happened", "任務尚未完成"), ("completion remains false", "任務仍未完成")),
    ("completed", True): (("the task is already complete", "the objective has been resolved", "completion is confirmed", "任務已完成"), ("completion is already true", "任務已經完成")),
}


def _reference_action(state: dict[str, object]) -> str | None:
    """Fast mirror of the frozen public policy for state-space enumeration.

    Every selected state is subsequently checked against the repository oracle;
    this function is not the authoritative label source.
    """
    if state["side_effect"] == "external" and state["permission"] == "not_required":
        return None
    if state["side_effect"] == "none" and state["permission"] != "not_required":
        return None
    if state["completed"]:
        return "IGNORE"
    if state["need"] == "none" and not state["deferral_available"]:
        return "IGNORE"
    if state["need"] == "none" and state["deferral_available"]:
        return "WAIT"
    if state["information"] != "sufficient" and state["clarification_possible"] and state["need"] != "none":
        return "ASK"
    if state["information"] != "sufficient" and not state["clarification_possible"] and state["urgency"] in ("high", "expired") and state["need"] == "material":
        return "NOTIFY"
    if state["information"] != "sufficient" and not state["clarification_possible"]:
        return "WAIT"
    if state["acknowledged"] and state["urgency"] not in ("high", "expired") and state["deferral_available"] and state["need"] != "none":
        return "WAIT"
    if state["urgency"] == "expired" and state["need"] == "material":
        return "NOTIFY"
    if state["side_effect"] == "external" and state["permission"] == "missing" and state["need"] == "material":
        return "ASK"
    if state["side_effect"] == "local" and state["permission"] == "missing" and state["need"] == "material":
        return "ASK"
    if state["side_effect"] != "none" and state["risk"] in ("medium", "high") and state["need"] == "material":
        return "ASK"
    if state["side_effect"] != "none" and state["reversibility"] == "irreversible" and state["need"] == "material":
        return "ASK"
    if state["side_effect"] == "external" and state["permission"] == "granted" and state["information"] == "sufficient" and state["risk"] == "low" and state["reversibility"] == "reversible" and state["execution_possible"] and state["need"] == "material":
        return "ACT"
    if state["side_effect"] == "local" and state["permission"] in ("not_required", "granted") and state["information"] == "sufficient" and state["risk"] == "low" and state["reversibility"] == "reversible" and state["execution_possible"] and state["need"] == "material":
        return "ACT"
    if state["need"] == "material" and state["urgency"] == "high":
        return "NOTIFY"
    if state["need"] == "material" and state["urgency"] == "normal":
        return "NOTIFY"
    if state["need"] == "material" and state["urgency"] == "none" and state["deferral_available"]:
        return "WAIT"
    if state["need"] == "material":
        return "SUGGEST"
    if state["need"] == "optional":
        return "SUGGEST"
    return "IGNORE"


def balanced_state_pool() -> dict[str, list[dict[str, object]]]:
    buckets: dict[str, list[dict[str, object]]] = {action: [] for action in ACTIONS}
    for combination in itertools.product(*(VALUES[field] for field in FIELDS)):
        state = dict(zip(FIELDS, combination))
        action = _reference_action(state)
        if action is not None:
            buckets[action].append(state)
    rng = random.Random(SEED)
    spec = load_spec()
    selected: dict[str, list[dict[str, object]]] = {}
    for action in ACTIONS:
        rng.shuffle(buckets[action])
        states = buckets[action][:48]
        if len(states) != 48:
            raise RuntimeError(f"insufficient states for {action}: {len(states)}")
        # The repository oracle is authoritative for selected Candidate-v4 states.
        for state in states:
            result = evaluate(state, spec=spec)
            if result.status != "VALID_DECISION" or result.action != action:
                raise AssertionError(f"oracle/reference mismatch for {action}: {state} -> {result}")
        selected[action] = states
    return selected


def _is_zh(text: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in text)


def _pick_phrase(field: str, value: object, mode: str, language: str, rng: random.Random) -> str:
    train, holdout = PHRASES[(field, value)]
    pool = train if mode == "train" else holdout
    if language == "zh":
        candidates = [item for item in pool if _is_zh(item)]
    elif language == "en":
        candidates = [item for item in pool if not _is_zh(item)]
    else:
        candidates = list(pool)
    return rng.choice(candidates or list(pool))


def render_state(state: dict[str, object], *, family: str, mode: str, rng: random.Random) -> str:
    phrases: list[str] = []
    for index, field in enumerate(FIELDS):
        if family == "zh_tw":
            language = "zh"
        elif family == "code_switch":
            language = "zh" if index % 3 == 0 else "en"
        else:
            language = "en"
        phrases.append(_pick_phrase(field, state[field], mode, language, rng))
    rng.shuffle(phrases)
    if family == "canonical":
        return ". ".join(phrases) + "."
    if family == "narrative":
        return "Current situation: " + "; ".join(phrases) + "."
    if family == "dialogue":
        return "Status check — " + " / ".join(phrases) + "."
    if family == "code_switch":
        return "Context／目前狀況: " + "；".join(phrases) + "。"
    if family == "telegraphic":
        return " | ".join(phrases)
    if family == "idiomatic":
        return "Plain-language read: " + "; ".join(phrases) + "."
    if family == "zh_tw":
        return "目前狀況：" + "；".join(phrases) + "。"
    if family == "embedded":
        return "Given that " + ", while ".join(phrases[:6]) + "; additionally " + ", and ".join(phrases[6:]) + "."
    raise ValueError(f"unknown rendering family: {family}")


def _record(action: str, state: dict[str, object], observation: str, split: str, index: int, family: str) -> dict[str, object]:
    return {
        "id": f"v4-{split}-{action.lower()}-{index:03d}",
        "domain": "development-safe-synthetic",
        "observation": observation,
        "expected_action": action,
        "state": deepcopy(state),
        "rendering_family": family,
    }


def build_splits() -> dict[str, list[dict[str, object]]]:
    pool = balanced_state_pool()
    split_specs = {
        "validation": (24, 30, "telegraphic", "train", 101),
        "ood": (30, 36, "idiomatic", "holdout", 102),
        "lexical_holdout": (36, 40, "canonical", "holdout", 103),
        "rendering_holdout": (40, 44, "zh_tw", "holdout", 104),
        "compositional_holdout": (44, 48, "embedded", "holdout", 105),
    }
    result: dict[str, list[dict[str, object]]] = {}
    training: list[dict[str, object]] = []
    rng_train = random.Random(SEED + 1)
    for action in ACTIONS:
        counter = 0
        for state in pool[action][:24]:
            for family in ("canonical", "narrative", "dialogue", "code_switch"):
                observation = render_state(state, family=family, mode="train", rng=rng_train)
                training.append(_record(action, state, observation, "train", counter, family))
                counter += 1
    result["train"] = training
    for split, (start, stop, family, mode, offset) in split_specs.items():
        rng = random.Random(SEED + offset)
        records: list[dict[str, object]] = []
        for action in ACTIONS:
            for local_index, state in enumerate(pool[action][start:stop]):
                observation = render_state(state, family=family, mode=mode, rng=rng)
                records.append(_record(action, state, observation, split, local_index, family))
        result[split] = records
    return result


def factor_supervision() -> list[tuple[str, str, object]]:
    rows: list[tuple[str, str, object]] = []
    for (field, value), (training, _holdout) in PHRASES.items():
        for phrase in training:
            rows.append((phrase, field, value))
    return rows


def build_counterfactual_pairs() -> list[dict[str, object]]:
    pool = balanced_state_pool()
    spec = load_spec()
    rng = random.Random(SEED + 300)
    pairs: list[dict[str, object]] = []
    mutations = (
        ("risk", "high"),
        ("information", "insufficient"),
        ("permission", "missing"),
    )
    for index, base in enumerate(pool["ACT"][24:30]):
        for mutation_index, (field, value) in enumerate(mutations):
            changed = deepcopy(base)
            changed[field] = value
            if field == "information":
                changed["clarification_possible"] = True
            before_result = evaluate(base, spec=spec)
            after_result = evaluate(changed, spec=spec)
            if before_result.action != "ACT" or after_result.action == "ACT" or after_result.status != "VALID_DECISION":
                raise AssertionError(f"invalid counterfactual pair: {field} {base} -> {changed}")
            before = _record("ACT", base, render_state(base, family="canonical", mode="holdout", rng=rng), "counterfactual", index * 3 + mutation_index, "canonical")
            after = _record(str(after_result.action), changed, render_state(changed, family="canonical", mode="holdout", rng=rng), "counterfactual", index * 3 + mutation_index, "canonical")
            pairs.append({"mutation": field, "before": before, "after": after})
    return pairs


def build_invariance_pairs() -> list[dict[str, object]]:
    pool = balanced_state_pool()
    rng_a = random.Random(SEED + 400)
    rng_b = random.Random(SEED + 401)
    pairs: list[dict[str, object]] = []
    for action in ACTIONS:
        for index, state in enumerate(pool[action][24:28]):
            left = _record(action, state, render_state(state, family="canonical", mode="train", rng=rng_a), "invariance", index, "canonical")
            right_family = "zh_tw" if index % 2 == 0 else "telegraphic"
            right_mode = "holdout" if right_family == "zh_tw" else "train"
            right = _record(action, state, render_state(state, family=right_family, mode=right_mode, rng=rng_b), "invariance", index, right_family)
            pairs.append({"left": left, "right": right})
    return pairs


def candidate_view(record: dict[str, object]) -> dict[str, object]:
    """Strip all latent/private development fields before inference."""
    return {"domain": record["domain"], "observation": record["observation"]}


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_json(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def generation_manifest() -> dict[str, object]:
    splits = build_splits()
    counterfactual = build_counterfactual_pairs()
    invariance = build_invariance_pairs()
    return {
        "seed": SEED,
        "split_sizes": {name: len(records) for name, records in splits.items()},
        "split_hashes": {name: sha256_json(records) for name, records in splits.items()},
        "counterfactual_pairs": len(counterfactual),
        "counterfactual_sha256": sha256_json(counterfactual),
        "invariance_pairs": len(invariance),
        "invariance_sha256": sha256_json(invariance),
        "factor_supervision_sha256": sha256_json(factor_supervision()),
    }
