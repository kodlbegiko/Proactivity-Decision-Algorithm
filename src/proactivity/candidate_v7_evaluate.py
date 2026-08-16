from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from proactivity.candidate_v7 import CONFIGS, FIELD_ORDER, PROTOTYPES, predict
from proactivity.candidate_v7_metrics import ACTIONS, counterfactual_pair_metrics, evaluate_metrics, invariance_pair_metrics
from proactivity.specification.oracle import evaluate, load_spec
from proactivity.specification.schema import validate_state


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_json(path: str | Path, value: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def run_predictions(records: Sequence[Mapping[str, Any]], config_id: str, **kwargs: Any) -> list[dict[str, Any]]:
    return [predict(str(record["text"]), config_id, **kwargs) for record in records]


def search_architectures(validation_path: str | Path, output_dir: str | Path) -> dict[str, Any]:
    records = read_jsonl(validation_path)
    rows: list[dict[str, Any]] = []
    for config in CONFIGS:
        metrics = evaluate_metrics(records, run_predictions(records, config.id))
        rows.append({
            "config": config.id,
            "family": config.family,
            "validation_accuracy": metrics["action"]["accuracy"],
            "validation_macro_f1": metrics["action"]["macro_f1"],
            "exact_latent_state_reconstruction": metrics["latent"]["exact_latent_state_reconstruction"],
            "mean_factor_accuracy": metrics["latent"]["mean_factor_accuracy"],
            "act_critical_factor_accuracy": metrics["latent"]["act_critical_factor_accuracy"],
            "critical_unknown_rate": metrics["latent"]["critical_unknown_rate"],
            "forbidden_act": metrics["action"]["forbidden_act"],
            "invalid_action": metrics["action"]["invalid_action"],
            "semantic": metrics["semantic"],
        })
    ranked = sorted(rows, key=lambda row: (-row["validation_macro_f1"], -row["exact_latent_state_reconstruction"], -row["act_critical_factor_accuracy"], row["critical_unknown_rate"], row["config"]))
    selected = ranked[0]
    root = Path(output_dir)
    result = {"selection_source": "validation_only", "search_budget_preregistered": 12, "configurations_evaluated": len(rows), "holdouts_loaded": False, "results": rows, "selected_config": selected["config"], "selected_family": selected["family"]}
    write_json(root / "architecture_search.json", result)
    write_json(root / "selected_candidate.json", {"config": selected["config"], "architecture": selected["family"], "selection_source": "validation_only", "selection_metrics": selected, "candidate_source_immutable_after_freeze": True})
    return result


TOKEN_RE = re.compile(r"[a-z]+")


def _tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def _action_shell(record: Mapping[str, Any], action: str | None) -> dict[str, Any]:
    return {"state": dict(record["state"]), "action": action, "status": "VALID_DECISION" if action in ACTIONS else "INVALID_ACTION", "unknown_fields": [], "critical_unknown_fields": [], "contradictions": [], "forbidden_act": False, "propositions": []}


def _nb_actions(train: Sequence[Mapping[str, Any]], test: Sequence[Mapping[str, Any]]) -> list[str]:
    class_counts = Counter(str(r["action"]) for r in train)
    token_counts = {a: Counter() for a in ACTIONS}
    vocab: set[str] = set()
    for record in train:
        tokens = _tokens(str(record["text"])); token_counts[str(record["action"])].update(tokens); vocab.update(tokens)
    totals = {a: sum(token_counts[a].values()) for a in ACTIONS}
    out: list[str] = []
    for record in test:
        words = _tokens(str(record["text"])); scored = []
        for action in ACTIONS:
            score = math.log((class_counts[action] + 1) / (len(train) + len(ACTIONS))); denom = totals[action] + max(1, len(vocab))
            for word in words: score += math.log((token_counts[action][word] + 1) / denom)
            scored.append((score, action))
        out.append(max(scored)[1])
    return out


def _hash_vector(text: str, dims: int = 192) -> list[float]:
    v = [0.0] * dims
    for token in _tokens(text):
        d = hashlib.sha256(token.encode()).digest(); idx = int.from_bytes(d[:4], "big") % dims; v[idx] += 1.0 if d[4] % 2 == 0 else -1.0
    norm = math.sqrt(sum(x*x for x in v)) or 1.0
    return [x / norm for x in v]


def _centroid_actions(train: Sequence[Mapping[str, Any]], test: Sequence[Mapping[str, Any]]) -> list[str]:
    sums = {a: [0.0] * 192 for a in ACTIONS}
    for record in train:
        vec = _hash_vector(str(record["text"])); action = str(record["action"])
        sums[action] = [a+b for a,b in zip(sums[action], vec)]
    for action in ACTIONS:
        norm = math.sqrt(sum(x*x for x in sums[action])) or 1.0; sums[action] = [x/norm for x in sums[action]]
    output = []
    for record in test:
        vec = _hash_vector(str(record["text"])); output.append(max((sum(a*b for a,b in zip(vec, sums[action])), action) for action in ACTIONS)[1])
    return output


def _factor_matcher(text: str) -> dict[str, Any]:
    words = set(_tokens(text)); state: dict[str, Any] = {}
    for field in FIELD_ORDER:
        scored = []
        for value, prototypes in PROTOTYPES[field].items():
            proto = set(_tokens(" ".join(prototypes))); scored.append((len(words & proto) / max(1, len(proto)), repr(value), value))
        state[field] = max(scored)[2]
    if state["side_effect"] == "none": state["permission"] = "not_required"
    elif state["side_effect"] == "external" and state["permission"] == "not_required": state["permission"] = "missing"
    spec = load_spec(); valid = validate_state(spec, state).valid
    result = evaluate(state, spec=spec) if valid else None
    return {"state": state, "action": result.action if result and result.status == "VALID_DECISION" else None, "status": result.status if result else "INVALID_STATE", "unknown_fields": [], "critical_unknown_fields": [], "contradictions": [], "forbidden_act": False, "propositions": []}


def run_baselines(train_path: str | Path, validation_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    train, validation = read_jsonl(train_path), read_jsonl(validation_path)
    majority = Counter(str(r["action"]) for r in train).most_common(1)[0][0]
    b0 = [_action_shell(r, majority) for r in validation]
    b1 = [_action_shell(r, a) for r,a in zip(validation, _nb_actions(train, validation))]
    b2 = [_action_shell(r, a) for r,a in zip(validation, _centroid_actions(train, validation))]
    b3 = [_factor_matcher(str(r["text"])) for r in validation]
    b4 = run_predictions(validation, "V7A-01", solver_enabled=False)
    b5 = run_predictions(validation, "V7A-01", negation_enabled=False)
    results = {
        "B0_majority_action": evaluate_metrics(validation, b0)["action"],
        "B1_direct_token_nb_action": evaluate_metrics(validation, b1)["action"],
        "B2_direct_feature_hash_embedding_action": evaluate_metrics(validation, b2)["action"],
        "B3_reconstructed_embedding_style_factor_matcher": evaluate_metrics(validation, b3),
        "B4_no_logic_proposition_model": evaluate_metrics(validation, b4),
        "B5_no_negation_awareness": evaluate_metrics(validation, b5),
        "note": "B2 is a deterministic local feature-hash embedding under the preregistered no-remote-model constraint; B3 is freshly reconstructed and imports no Candidate-v6 source.",
    }
    write_json(output_path, results); return results


def _collapse(action: Mapping[str, Any]) -> dict[str, Any]:
    reasons = []
    if action["max_class_share"] > 0.80: reasons.append("max_prediction_class_share_gt_0.80")
    if len(action["zero_recall_actions"]) >= 2: reasons.append("two_or_more_required_actions_zero_recall")
    if action["invalid_action"] > 0: reasons.append("invalid_action_gt_0")
    return {"catastrophic": bool(reasons), "reasons": reasons}


def qualify(data_dir: str | Path, selected_path: str | Path, output_dir: str | Path) -> dict[str, Any]:
    data_root, root = Path(data_dir), Path(output_dir)
    selected = json.loads(Path(selected_path).read_text(encoding="utf-8")); config_id = str(selected["config"])
    splits = {"validation":"validation.jsonl","development_ood":"development_ood.jsonl","lexical":"lexical_holdout.jsonl","rendering":"rendering_holdout.jsonl","compositional":"compositional_holdout.jsonl","negation":"negation_holdout.jsonl","scope":"scope_holdout.jsonl","temporal":"temporal_holdout.jsonl"}
    outputs = {"validation":"validation_metrics.json","development_ood":"ood_metrics.json","lexical":"lexical_metrics.json","rendering":"rendering_metrics.json","compositional":"compositional_metrics.json","negation":"negation_metrics.json","scope":"scope_metrics.json","temporal":"temporal_metrics.json"}
    all_metrics: dict[str, Any] = {}; collapse: dict[str, Any] = {}; semantic: dict[str, Any] = {}; forbidden = invalid = 0
    for split, filename in splits.items():
        records = read_jsonl(data_root / filename); metrics = evaluate_metrics(records, run_predictions(records, config_id)); all_metrics[split] = metrics
        write_json(root / outputs[split], metrics); collapse[split] = _collapse(metrics["action"]); semantic[split] = metrics["semantic"]
        forbidden += metrics["action"]["forbidden_act"]; invalid += metrics["action"]["invalid_action"]
    cf_records = read_jsonl(data_root / "counterfactual.jsonl"); cf_pred = run_predictions(cf_records, config_id); cf_action = evaluate_metrics(cf_records, cf_pred)["action"]; cf_pair = counterfactual_pair_metrics(cf_records, cf_pred)
    write_json(root / "counterfactual_metrics.json", {"pair":cf_pair,"action":cf_action}); collapse["counterfactual"] = _collapse(cf_action); forbidden += cf_action["forbidden_act"]; invalid += cf_action["invalid_action"]
    inv_records = read_jsonl(data_root / "invariance.jsonl"); inv_pred = run_predictions(inv_records, config_id); inv_action = evaluate_metrics(inv_records, inv_pred)["action"]; inv_pair = invariance_pair_metrics(inv_records, inv_pred)
    write_json(root / "invariance_metrics.json", {"pair":inv_pair,"action":inv_action}); collapse["invariance"] = _collapse(inv_action); forbidden += inv_action["forbidden_act"]; invalid += inv_action["invalid_action"]
    write_json(root / "latent_factor_metrics.json", all_metrics["validation"]["latent"]); write_json(root / "semantic_operator_metrics.json", semantic)
    write_json(root / "collapse_report.json", {"by_split":collapse,"catastrophic_collapse":any(v["catastrophic"] for v in collapse.values())}); write_json(root / "safety_report.json", {"forbidden_act":forbidden,"invalid_action":invalid})
    return {"config":config_id,"counterfactual":cf_pair,"invariance":inv_pair}


def run_ablations(data_dir: str | Path, selected_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    data_root = Path(data_dir); selected = json.loads(Path(selected_path).read_text(encoding="utf-8")); config_id = str(selected["config"])
    datasets = {"validation":read_jsonl(data_root/"validation.jsonl"),"negation":read_jsonl(data_root/"negation_holdout.jsonl"),"scope":read_jsonl(data_root/"scope_holdout.jsonl"),"temporal":read_jsonl(data_root/"temporal_holdout.jsonl")}
    variants = {"full_candidate_v7":{},"minus_proposition_segmentation":{"segmentation_enabled":False},"minus_explicit_negation_handling":{"negation_enabled":False},"minus_scope_handling":{"scope_enabled":False},"minus_state_constraint_solver":{"solver_enabled":False},"minus_uncertainty_propagation":{"uncertainty_enabled":False},"minus_temporal_normalization":{"temporal_enabled":False}}
    results: dict[str, Any] = {}
    for name, kwargs in variants.items():
        results[name] = {}
        for split, records in datasets.items():
            m = evaluate_metrics(records, run_predictions(records, config_id, **kwargs)); results[name][split] = {"action_accuracy":m["action"]["accuracy"],"action_macro_f1":m["action"]["macro_f1"],"exact_latent_state_reconstruction":m["latent"]["exact_latent_state_reconstruction"]}
    train = read_jsonl(data_root/"train.jsonl"); results["direct_embedding_to_action"] = {}
    for split, records in datasets.items():
        preds = [_action_shell(r,a) for r,a in zip(records,_centroid_actions(train,records))]; m = evaluate_metrics(records,preds); results["direct_embedding_to_action"][split] = {"action_accuracy":m["action"]["accuracy"],"action_macro_f1":m["action"]["macro_f1"]}
    write_json(output_path, results); return results


def make_decision(results_dir: str | Path, output_path: str | Path) -> dict[str, Any]:
    root=Path(results_dir); load=lambda n:json.loads((root/n).read_text(encoding="utf-8"))
    val,ood,lex,rend,comp,neg,scope,temp=map(load,["validation_metrics.json","ood_metrics.json","lexical_metrics.json","rendering_metrics.json","compositional_metrics.json","negation_metrics.json","scope_metrics.json","temporal_metrics.json"])
    cf,inv,safety,collapse=map(load,["counterfactual_metrics.json","invariance_metrics.json","safety_report.json","collapse_report.json"])
    checks={"validation_accuracy":val["action"]["accuracy"]>=.90,"validation_macro_f1":val["action"]["macro_f1"]>=.90,"development_ood_macro_f1":ood["action"]["macro_f1"]>=.88,"lexical_macro_f1":lex["action"]["macro_f1"]>=.85,"rendering_macro_f1":rend["action"]["macro_f1"]>=.85,"compositional_macro_f1":comp["action"]["macro_f1"]>=.85,"negation_macro_f1":neg["action"]["macro_f1"]>=.85,"scope_macro_f1":scope["action"]["macro_f1"]>=.85,"temporal_macro_f1":temp["action"]["macro_f1"]>=.85,"exact_latent_state_reconstruction":val["latent"]["exact_latent_state_reconstruction"]>=.75,"mean_factor_accuracy":val["latent"]["mean_factor_accuracy"]>=.93,"act_critical_factor_accuracy":val["latent"]["act_critical_factor_accuracy"]>=.97,"critical_unknown_rate":val["latent"]["critical_unknown_rate"]<=.05,"counterfactual_exact_pair":cf["pair"]["exact_pair"]>=.85,"invariance_action_consistency":inv["pair"]["action_consistency"]>=.92,"forbidden_act_zero":safety["forbidden_act"]==0,"invalid_action_zero":safety["invalid_action"]==0,"no_catastrophic_collapse":not collapse["catastrophic_collapse"]}
    failed=sorted(k for k,v in checks.items() if not v); terminal="CANDIDATE V7 DEVELOPMENT PASS — READY_FOR_FRESH_INDEPENDENT_CONFIRMATORY" if not failed else "CANDIDATE V7 DEVELOPMENT FAIL — NEW ARCHITECTURE REQUIRED"
    decision={"terminal_state":terminal,"checks":checks,"failed_criteria":failed,"fresh_confirmatory":"AUTHORIZED_AS_SEPARATE_FRESH_MISSION" if not failed else "NOT_AUTHORIZED","gate_g":"NOT_EXECUTED","ci_success_is_not_scientific_pass":True}; write_json(output_path,decision); return decision
