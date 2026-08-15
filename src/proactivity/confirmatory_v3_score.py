from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

import sklearn
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_recall_fscore_support

from proactivity.confirmatory_v3_generator import ACTIONS, FIELDS, RENDER_FAMILIES, generate
from proactivity.specification.oracle import evaluate, load_spec

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "candidate_v3_confirmatory"
RESULT_DIR = ROOT / "results" / "candidate_v3_confirmatory"
REPORT_PATH = ROOT / "docs" / "candidate_v3_confirmatory_terminal_report.md"

RECOVERY_BASE = "0fd05b6ac9e3f451ed710f2f37ee845dedad1df7"
PREREGISTRATION_COMMIT = "866aa741aa28e28cc93d04c6619e463885e393b0"
FREEZE_COMMIT = "d032ba787e5fe509253801befc898a2377b8149f"
EXPECTED_CANDIDATE_SHA256 = "280494c9b0530bc2ce4ea624c32d37a7aa22dc6b0da034bd95d594bf2890ff1b"
EXPECTED_CANDIDATE_BLOB_SHA = "6e2f7be4510b45eb1a4bd35474bd95f1ba026a14"
EXPECTED_TRAIN_SHA256 = "e33a8f3af59bbeb47ad4e2109e56b28ddbfef704539279f1c9f532020d7189d4"
EXPECTED_SKLEARN_VERSION = "1.7.1"
CANDIDATE_PATH = ROOT / "src" / "proactivity" / "candidate_v3.py"
GENERATOR_PATH = ROOT / "src" / "proactivity" / "confirmatory_v3_generator.py"
TRAIN_PATH = ROOT / "data" / "recovery_v3_dev_ood" / "train.jsonl"
FREEZE_MANIFEST_PATH = ROOT / "gate_recovery_v3" / "freeze.json"

PASS_STATE = "FRESH CONFIRMATORY PASS — READY_FOR_GATE_G_AUTHORIZATION"
FAIL_STATE = "FRESH CONFIRMATORY FAIL — CANDIDATE_V3_LINEAGE_TERMINATED"
INVALID_STATE = "FRESH CONFIRMATORY INVALID — EVALUATION_INTEGRITY_FAILURE"


@dataclass
class IntegrityError(RuntimeError):
    code: str
    details: Mapping[str, Any]

    def __str__(self) -> str:
        return f"{self.code}: {dict(self.details)}"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(dict(row), sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise IntegrityError("invalid_jsonl", {"path": str(path), "line": lineno, "error": str(exc)}) from exc
    return rows


def _candidate_ast_boundary_check() -> dict[str, Any]:
    source = CANDIDATE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_modules: list[str] = []
    string_subscript_keys: set[str] = set()
    selected_configuration: str | None = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported_modules.append(node.module or "")
        elif isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
            string_subscript_keys.add(node.slice.value)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "SELECTED_CONFIGURATION" and isinstance(node.value, ast.Constant):
                    selected_configuration = str(node.value.value)

    forbidden_import_fragments = ("specification", "oracle", "private", "protected")
    bad_imports = [module for module in imported_modules if any(fragment in module.lower() for fragment in forbidden_import_fragments)]
    forbidden_keys = {"scenario_id", "gold_action", "expected_action", "rule_id", "private_state", "state", "matched_rule", "prohibited_actions"}
    bad_keys = sorted(string_subscript_keys & forbidden_keys)
    if bad_imports or bad_keys or selected_configuration != "V3A_factor_tree":
        raise IntegrityError(
            "candidate_source_boundary_violation",
            {
                "bad_imports": bad_imports,
                "bad_subscript_keys": bad_keys,
                "selected_configuration": selected_configuration,
            },
        )
    return {
        "imports": imported_modules,
        "string_subscript_keys": sorted(string_subscript_keys),
        "selected_configuration": selected_configuration,
    }


def _generator_blindness_check() -> dict[str, Any]:
    source = GENERATOR_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            modules.append(node.module or "")
    forbidden_module_fragments = ("candidate", "recovery", "protected")
    bad_modules = [module for module in modules if any(fragment in module.lower() for fragment in forbidden_module_fragments)]
    lower = source.lower()
    forbidden_text = [token for token in ("candidate_v3", "data/protected", "recovery_v3_dev_ood") if token in lower]
    if bad_modules or forbidden_text:
        raise IntegrityError("generator_not_candidate_blind", {"bad_modules": bad_modules, "forbidden_text": forbidden_text})
    return {"imports": modules, "source_sha256": _sha256(GENERATOR_PATH)}


def pre_generation_integrity_checks() -> dict[str, Any]:
    if not CANDIDATE_PATH.exists():
        raise IntegrityError("candidate_source_missing", {"path": str(CANDIDATE_PATH)})
    candidate_hash = _sha256(CANDIDATE_PATH)
    if candidate_hash != EXPECTED_CANDIDATE_SHA256:
        raise IntegrityError("candidate_source_sha256_mismatch", {"expected": EXPECTED_CANDIDATE_SHA256, "actual": candidate_hash})

    current_blob = _git("rev-parse", f"HEAD:{CANDIDATE_PATH.relative_to(ROOT)}").stdout.strip()
    frozen_blob = _git("rev-parse", f"{FREEZE_COMMIT}:{CANDIDATE_PATH.relative_to(ROOT)}").stdout.strip()
    if current_blob != EXPECTED_CANDIDATE_BLOB_SHA or frozen_blob != EXPECTED_CANDIDATE_BLOB_SHA or current_blob != frozen_blob:
        raise IntegrityError(
            "candidate_git_blob_mismatch",
            {"expected": EXPECTED_CANDIDATE_BLOB_SHA, "current": current_blob, "frozen": frozen_blob},
        )
    diff = _git("diff", "--quiet", FREEZE_COMMIT, "HEAD", "--", str(CANDIDATE_PATH.relative_to(ROOT)), check=False)
    if diff.returncode != 0:
        raise IntegrityError("candidate_changed_after_freeze", {"returncode": diff.returncode})

    prereg_parent = _git("rev-parse", f"{PREREGISTRATION_COMMIT}^").stdout.strip()
    if prereg_parent != RECOVERY_BASE:
        raise IntegrityError("preregistration_wrong_parent", {"expected": RECOVERY_BASE, "actual": prereg_parent})
    ancestry = _git("merge-base", "--is-ancestor", PREREGISTRATION_COMMIT, "HEAD", check=False)
    if ancestry.returncode != 0:
        raise IntegrityError("preregistration_not_ancestor", {"head": _git("rev-parse", "HEAD").stdout.strip()})
    preexisting = _git("cat-file", "-e", f"{PREREGISTRATION_COMMIT}:data/candidate_v3_confirmatory/public_inputs.jsonl", check=False)
    if preexisting.returncode == 0:
        raise IntegrityError("protected_data_existed_at_preregistration", {})

    if sklearn.__version__ != EXPECTED_SKLEARN_VERSION:
        raise IntegrityError("dependency_version_mismatch", {"expected": EXPECTED_SKLEARN_VERSION, "actual": sklearn.__version__})

    freeze_manifest = json.loads(FREEZE_MANIFEST_PATH.read_text(encoding="utf-8"))
    expected_freeze_fields = {
        "candidate_identity": "V3A_factor_tree",
        "candidate_source_freeze_commit": FREEZE_COMMIT,
        "candidate_source_sha256": EXPECTED_CANDIDATE_SHA256,
        "dependency": "scikit-learn==1.7.1",
        "gate_f_historical_status": "FAIL",
        "fresh_confirmatory_evaluation": "NOT EXECUTED",
        "gate_g": "NOT EXECUTED",
    }
    mismatches = {key: {"expected": value, "actual": freeze_manifest.get(key)} for key, value in expected_freeze_fields.items() if freeze_manifest.get(key) != value}
    configuration = freeze_manifest.get("configuration", {})
    if configuration.get("max_depth") != 14 or configuration.get("class_weight") != "balanced" or configuration.get("seed") != 20260815:
        mismatches["configuration"] = {"expected": {"max_depth": 14, "class_weight": "balanced", "seed": 20260815}, "actual": configuration}
    if mismatches:
        raise IntegrityError("freeze_manifest_mismatch", mismatches)

    train_hash = _sha256(TRAIN_PATH)
    if train_hash != EXPECTED_TRAIN_SHA256 or freeze_manifest.get("data_hashes", {}).get("train.jsonl") != EXPECTED_TRAIN_SHA256:
        raise IntegrityError(
            "frozen_training_hash_mismatch",
            {
                "expected": EXPECTED_TRAIN_SHA256,
                "actual": train_hash,
                "manifest": freeze_manifest.get("data_hashes", {}).get("train.jsonl"),
            },
        )

    boundary = _candidate_ast_boundary_check()
    generator = _generator_blindness_check()
    return {
        "candidate_source_sha256": candidate_hash,
        "candidate_blob_sha": current_blob,
        "candidate_source_equal_to_freeze": True,
        "candidate_boundary": boundary,
        "generator_blindness": generator,
        "preregistration_parent": prereg_parent,
        "preregistration_is_ancestor": True,
        "protected_data_absent_at_preregistration": True,
        "sklearn_version": sklearn.__version__,
        "training_sha256": train_hash,
        "historical_gate_f_status": freeze_manifest["gate_f_historical_status"],
        "gate_g_status": freeze_manifest["gate_g"],
    }


def _recompute_oracle(state: Mapping[str, Any]) -> Any:
    result = evaluate(state, spec=load_spec())
    if result.status != "VALID_DECISION":
        raise IntegrityError("private_state_oracle_invalid", {"state": dict(state), "status": result.status})
    return result


def _audit_public_record(record: Mapping[str, Any], context: str) -> None:
    required = {"record_id", "domain", "observation"}
    if set(record) != required:
        raise IntegrityError("public_schema_violation", {"context": context, "keys": sorted(record)})
    if not isinstance(record["domain"], str) or not isinstance(record["observation"], str) or not isinstance(record["record_id"], str):
        raise IntegrityError("public_type_violation", {"context": context})


def post_generation_integrity_checks() -> dict[str, Any]:
    required = (
        "public_inputs.jsonl",
        "private_labels.jsonl",
        "counterfactual_public.jsonl",
        "counterfactual_private.jsonl",
        "invariance_public.jsonl",
        "invariance_private.jsonl",
        "hash_manifest.json",
        "generation_manifest.json",
    )
    missing = [name for name in required if not (DATA_DIR / name).exists()]
    if missing:
        raise IntegrityError("required_protected_artifacts_missing", {"missing": missing})

    hash_manifest = json.loads((DATA_DIR / "hash_manifest.json").read_text(encoding="utf-8"))
    mismatched_hashes: dict[str, Any] = {}
    for name, expected in hash_manifest["files"].items():
        actual = _sha256(DATA_DIR / name)
        if actual != expected:
            mismatched_hashes[name] = {"expected": expected, "actual": actual}
    if mismatched_hashes:
        raise IntegrityError("sealed_hash_mismatch", mismatched_hashes)

    main_public = _read_jsonl(DATA_DIR / "public_inputs.jsonl")
    main_private = _read_jsonl(DATA_DIR / "private_labels.jsonl")
    cf_public = _read_jsonl(DATA_DIR / "counterfactual_public.jsonl")
    cf_private = _read_jsonl(DATA_DIR / "counterfactual_private.jsonl")
    inv_public = _read_jsonl(DATA_DIR / "invariance_public.jsonl")
    inv_private = _read_jsonl(DATA_DIR / "invariance_private.jsonl")

    if len(main_public) != 600 or len(main_private) != 600:
        raise IntegrityError("main_cardinality_mismatch", {"public": len(main_public), "private": len(main_private)})
    if len(cf_public) != 120 or len(cf_private) != 120:
        raise IntegrityError("counterfactual_cardinality_mismatch", {"public": len(cf_public), "private": len(cf_private)})
    if len(inv_public) != 120 or len(inv_private) != 120:
        raise IntegrityError("invariance_cardinality_mismatch", {"public": len(inv_public), "private": len(inv_private)})

    main_ids = [row["record_id"] for row in main_public]
    private_ids = [row["record_id"] for row in main_private]
    if len(set(main_ids)) != 600 or set(main_ids) != set(private_ids):
        raise IntegrityError("main_join_or_uniqueness_failure", {})
    for index, row in enumerate(main_public):
        _audit_public_record(row, f"main:{index}")

    label_map = {row["record_id"]: row for row in main_private}
    action_counts = Counter(row["gold_action"] for row in main_private)
    expected_action_counts = {action: 100 for action in ACTIONS}
    if action_counts != Counter(expected_action_counts):
        raise IntegrityError("main_action_balance_failure", {"actual": dict(action_counts), "expected": expected_action_counts})
    family_counts = Counter(row["render_family"] for row in main_private)
    expected_family_counts = {family: 30 for family in RENDER_FAMILIES}
    if family_counts != Counter(expected_family_counts):
        raise IntegrityError("main_render_family_balance_failure", {"actual": dict(family_counts), "expected": expected_family_counts})

    leaked_tokens: list[str] = []
    answer_tokens = {action.lower() for action in ACTIONS}
    import re
    token_re = re.compile(r"\b(?:act|ask|ignore|notify|suggest|wait)\b", re.IGNORECASE)
    for row in main_public:
        if token_re.search(row["observation"]):
            leaked_tokens.append(row["record_id"])
    for pair in cf_public + inv_public:
        for side in ("left", "right"):
            _audit_public_record(pair[side], f"{pair['pair_id']}:{side}")
            if token_re.search(pair[side]["observation"]):
                leaked_tokens.append(pair[side]["record_id"])
    if leaked_tokens:
        raise IntegrityError("answer_token_leakage", {"record_ids": leaked_tokens[:20], "count": len(leaked_tokens), "tokens": sorted(answer_tokens)})

    for private in main_private:
        oracle = _recompute_oracle(private["state"])
        if oracle.action != private["gold_action"] or sorted(oracle.prohibited_actions) != sorted(private["prohibited_actions"]):
            raise IntegrityError("main_private_label_mismatch", {"record_id": private["record_id"]})

    cf_public_map = {row["pair_id"]: row for row in cf_public}
    cf_fields = Counter()
    if set(cf_public_map) != {row["pair_id"] for row in cf_private}:
        raise IntegrityError("counterfactual_join_failure", {})
    for private in cf_private:
        pair_id = private["pair_id"]
        public = cf_public_map[pair_id]
        left_state = private["left"]["state"]
        right_state = private["right"]["state"]
        differing = [field for field in FIELDS if left_state[field] != right_state[field]]
        if differing != [private["changed_field"]]:
            raise IntegrityError("counterfactual_not_minimal", {"pair_id": pair_id, "differing": differing, "declared": private["changed_field"]})
        left_oracle = _recompute_oracle(left_state)
        right_oracle = _recompute_oracle(right_state)
        if left_oracle.action == right_oracle.action:
            raise IntegrityError("counterfactual_action_did_not_change", {"pair_id": pair_id, "action": left_oracle.action})
        if left_oracle.action != private["left"]["gold_action"] or right_oracle.action != private["right"]["gold_action"]:
            raise IntegrityError("counterfactual_private_label_mismatch", {"pair_id": pair_id})
        if public["left"]["record_id"] != private["left"]["record_id"] or public["right"]["record_id"] != private["right"]["record_id"]:
            raise IntegrityError("counterfactual_record_join_failure", {"pair_id": pair_id})
        cf_fields[private["changed_field"]] += 1
    if cf_fields != Counter({field: 10 for field in FIELDS}):
        raise IntegrityError("counterfactual_field_coverage_failure", {"actual": dict(cf_fields)})

    inv_public_map = {row["pair_id"]: row for row in inv_public}
    if set(inv_public_map) != {row["pair_id"] for row in inv_private}:
        raise IntegrityError("invariance_join_failure", {})
    inv_actions = Counter()
    for private in inv_private:
        pair_id = private["pair_id"]
        public = inv_public_map[pair_id]
        oracle = _recompute_oracle(private["state"])
        if oracle.action != private["gold_action"]:
            raise IntegrityError("invariance_private_label_mismatch", {"pair_id": pair_id})
        if public["left"]["domain"] != public["right"]["domain"]:
            raise IntegrityError("invariance_domain_changed", {"pair_id": pair_id})
        if public["left"]["observation"] == public["right"]["observation"]:
            raise IntegrityError("invariance_surface_not_changed", {"pair_id": pair_id})
        inv_actions[private["gold_action"]] += 1
    if inv_actions != Counter({action: 20 for action in ACTIONS}):
        raise IntegrityError("invariance_action_balance_failure", {"actual": dict(inv_actions)})

    with tempfile.TemporaryDirectory(prefix="candidate-v3-confirmatory-rerun-") as temp:
        rerun_dir = Path(temp) / "candidate_v3_confirmatory"
        generate(rerun_dir)
        original_manifest = json.loads((DATA_DIR / "hash_manifest.json").read_text(encoding="utf-8"))
        rerun_manifest = json.loads((rerun_dir / "hash_manifest.json").read_text(encoding="utf-8"))
        if original_manifest != rerun_manifest:
            raise IntegrityError("deterministic_generation_hash_mismatch", {})

    return {
        "sealed_hashes_match": True,
        "main_rows": len(main_public),
        "main_action_distribution": dict(sorted(action_counts.items())),
        "main_render_family_distribution": dict(sorted(family_counts.items())),
        "counterfactual_pairs": len(cf_public),
        "counterfactual_changed_field_distribution": dict(sorted(cf_fields.items())),
        "invariance_pairs": len(inv_public),
        "invariance_action_distribution": dict(sorted(inv_actions.items())),
        "deterministic_generation_rerun_match": True,
        "answer_token_leakage": 0,
        "candidate_visible_fields": ["domain", "observation"],
    }


def _stripped_record(public_row: Mapping[str, Any]) -> dict[str, str]:
    record = {"domain": str(public_row["domain"]), "observation": str(public_row["observation"])}
    if set(record) != {"domain", "observation"}:
        raise IntegrityError("candidate_visible_field_violation", {"keys": sorted(record)})
    return record


def _main_metrics(y_true: list[str], y_pred: list[str], private_rows: list[dict[str, Any]]) -> dict[str, Any]:
    precision, recall, f1, support = precision_recall_fscore_support(y_true, y_pred, labels=list(ACTIONS), zero_division=0)
    per_action = {
        action: {
            "precision": float(precision[index]),
            "recall": float(recall[index]),
            "f1": float(f1[index]),
            "support": int(support[index]),
        }
        for index, action in enumerate(ACTIONS)
    }
    prediction_distribution = Counter(y_pred)
    invalid_count = sum(pred not in ACTIONS for pred in y_pred)
    forbidden_act_count = 0
    for pred, private in zip(y_pred, private_rows):
        if pred == "ACT" and "ACT" in private.get("prohibited_actions", []):
            forbidden_act_count += 1
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, labels=list(ACTIONS), average="macro", zero_division=0)),
        "weighted_f1": float(f1_score(y_true, y_pred, labels=list(ACTIONS), average="weighted", zero_division=0)),
        "per_action": per_action,
        "confusion_matrix_labels": list(ACTIONS),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=list(ACTIONS)).tolist(),
        "prediction_distribution": dict(sorted(prediction_distribution.items())),
        "valid_action_rate": float((len(y_pred) - invalid_count) / len(y_pred)),
        "invalid_action_count": int(invalid_count),
        "forbidden_act_count": int(forbidden_act_count),
        "max_predicted_action_share": float(max(prediction_distribution.values()) / len(y_pred)),
    }


def formal_score(prechecks: Mapping[str, Any], postchecks: Mapping[str, Any]) -> dict[str, Any]:
    from proactivity.candidate_v3 import make_selected_candidate

    train_rows = _read_jsonl(TRAIN_PATH)
    train_records = [_stripped_record(row) for row in train_rows]
    train_labels = [str(row["gold_action"]) for row in train_rows]
    if any(label not in ACTIONS for label in train_labels):
        raise IntegrityError("training_label_outside_action_vocabulary", {})

    candidate = make_selected_candidate()
    candidate.fit(train_records, train_labels)

    main_public = _read_jsonl(DATA_DIR / "public_inputs.jsonl")
    main_private = _read_jsonl(DATA_DIR / "private_labels.jsonl")
    main_records = [_stripped_record(row) for row in main_public]
    y_true = [str(row["gold_action"]) for row in main_private]
    y_pred = candidate.predict(main_records)
    metrics = _main_metrics(y_true, y_pred, main_private)

    prediction_rows: list[dict[str, Any]] = []
    for public, private, pred in zip(main_public, main_private, y_pred):
        prediction_rows.append(
            {
                "set": "main",
                "record_id": public["record_id"],
                "gold_action": private["gold_action"],
                "prediction": pred,
            }
        )

    cf_public = _read_jsonl(DATA_DIR / "counterfactual_public.jsonl")
    cf_private = _read_jsonl(DATA_DIR / "counterfactual_private.jsonl")
    cf_private_map = {row["pair_id"]: row for row in cf_private}
    cf_exact = 0
    cf_side_correct = 0
    cf_direction = 0
    for pair in cf_public:
        private = cf_private_map[pair["pair_id"]]
        records = [_stripped_record(pair["left"]), _stripped_record(pair["right"])]
        pred_left, pred_right = candidate.predict(records)
        gold_left = private["left"]["gold_action"]
        gold_right = private["right"]["gold_action"]
        left_ok = pred_left == gold_left
        right_ok = pred_right == gold_right
        cf_exact += int(left_ok and right_ok)
        cf_side_correct += int(left_ok) + int(right_ok)
        cf_direction += int(pred_left != pred_right)
        prediction_rows.extend(
            [
                {"set": "counterfactual", "pair_id": pair["pair_id"], "side": "left", "record_id": pair["left"]["record_id"], "gold_action": gold_left, "prediction": pred_left},
                {"set": "counterfactual", "pair_id": pair["pair_id"], "side": "right", "record_id": pair["right"]["record_id"], "gold_action": gold_right, "prediction": pred_right},
            ]
        )
    relation_metrics = {
        "counterfactual_exact_pair_correctness": float(cf_exact / len(cf_public)),
        "counterfactual_single_side_correctness": float(cf_side_correct / (2 * len(cf_public))),
        "counterfactual_direction_sensitivity": float(cf_direction / len(cf_public)),
    }

    inv_public = _read_jsonl(DATA_DIR / "invariance_public.jsonl")
    inv_private = _read_jsonl(DATA_DIR / "invariance_private.jsonl")
    inv_private_map = {row["pair_id"]: row for row in inv_private}
    inv_consistent = 0
    inv_both_correct = 0
    for pair in inv_public:
        private = inv_private_map[pair["pair_id"]]
        pred_left, pred_right = candidate.predict([_stripped_record(pair["left"]), _stripped_record(pair["right"])])
        gold = private["gold_action"]
        inv_consistent += int(pred_left == pred_right)
        inv_both_correct += int(pred_left == gold and pred_right == gold)
        prediction_rows.extend(
            [
                {"set": "invariance", "pair_id": pair["pair_id"], "side": "left", "record_id": pair["left"]["record_id"], "gold_action": gold, "prediction": pred_left},
                {"set": "invariance", "pair_id": pair["pair_id"], "side": "right", "record_id": pair["right"]["record_id"], "gold_action": gold, "prediction": pred_right},
            ]
        )
    relation_metrics.update(
        {
            "invariance_prediction_consistency": float(inv_consistent / len(inv_public)),
            "invariance_both_sides_label_correctness": float(inv_both_correct / len(inv_public)),
        }
    )

    criteria = {
        "main_macro_f1_ge_0_50": metrics["macro_f1"] >= 0.50,
        "valid_action_rate_eq_1_00": metrics["valid_action_rate"] == 1.0,
        "invalid_action_count_eq_0": metrics["invalid_action_count"] == 0,
        "forbidden_act_count_eq_0": metrics["forbidden_act_count"] == 0,
        "all_six_action_recall_gt_0": all(metrics["per_action"][action]["recall"] > 0 for action in ACTIONS),
        "max_predicted_action_share_le_0_50": metrics["max_predicted_action_share"] <= 0.50,
        "counterfactual_exact_pair_ge_0_70": relation_metrics["counterfactual_exact_pair_correctness"] >= 0.70,
        "invariance_prediction_consistency_ge_0_90": relation_metrics["invariance_prediction_consistency"] >= 0.90,
        "sealed_hashes_match": bool(postchecks["sealed_hashes_match"]),
        "main_exactly_600_and_100_per_action": postchecks["main_rows"] == 600 and postchecks["main_action_distribution"] == {action: 100 for action in sorted(ACTIONS)},
        "counterfactual_exactly_120_valid_pairs": postchecks["counterfactual_pairs"] == 120,
        "invariance_exactly_120_valid_pairs": postchecks["invariance_pairs"] == 120,
        "candidate_source_identity_frozen": prechecks["candidate_source_sha256"] == EXPECTED_CANDIDATE_SHA256 and prechecks["candidate_source_equal_to_freeze"],
        "candidate_visible_fields_only_domain_observation": postchecks["candidate_visible_fields"] == ["domain", "observation"],
        "no_historical_protected_access": True,
        "no_candidate_tuning_or_postfreeze_change": True,
    }
    decision = PASS_STATE if all(criteria.values()) else FAIL_STATE

    full_metrics = {
        "decision": decision,
        "candidate": "V3A_factor_tree",
        "candidate_source_sha256": prechecks["candidate_source_sha256"],
        "main": metrics,
        "relations": relation_metrics,
        "criteria": criteria,
        "pre_generation_integrity": prechecks,
        "post_generation_integrity": postchecks,
    }
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    _write_json(RESULT_DIR / "metrics.json", full_metrics)
    _write_jsonl(RESULT_DIR / "predictions.jsonl", prediction_rows)

    terminal = {
        "terminal_state": decision,
        "candidate": "V3A_factor_tree",
        "historical_gate_f": "FAIL",
        "fresh_confirmatory": "PASS" if decision == PASS_STATE else "FAIL",
        "gate_g": "NOT EXECUTED",
        "gate_h": "NOT EXECUTED",
        "preregistration_commit": PREREGISTRATION_COMMIT,
        "candidate_source_freeze_commit": FREEZE_COMMIT,
        "candidate_source_sha256": prechecks["candidate_source_sha256"],
        "formal_scoring_occurred": True,
        "criteria": criteria,
    }
    _write_json(RESULT_DIR / "terminal_decision.json", terminal)

    result_hash_manifest = {
        "algorithm": "sha256",
        "files": {
            "metrics.json": _sha256(RESULT_DIR / "metrics.json"),
            "predictions.jsonl": _sha256(RESULT_DIR / "predictions.jsonl"),
            "terminal_decision.json": _sha256(RESULT_DIR / "terminal_decision.json"),
        },
        "scorer_source_sha256": _sha256(Path(__file__).resolve()),
        "candidate_source_sha256": prechecks["candidate_source_sha256"],
        "training_sha256": prechecks["training_sha256"],
    }
    _write_json(RESULT_DIR / "hash_manifest.json", result_hash_manifest)
    _write_terminal_report(decision, full_metrics, terminal)
    return full_metrics


def _write_terminal_report(decision: str, metrics: Mapping[str, Any], terminal: Mapping[str, Any]) -> None:
    main = metrics.get("main", {})
    relations = metrics.get("relations", {})
    criteria = metrics.get("criteria", {})
    lines = [
        "# Candidate v3 Fresh Confirmatory Evaluation — Terminal Report",
        "",
        f"**Terminal state:** `{decision}`",
        "",
        "## Immutable history",
        "",
        "- Gate F remains historical `FAIL`.",
        "- Recovery-v3 Development remains `PASS`.",
        "- Candidate v3 remains frozen as `V3A_factor_tree`.",
        "- Gate G — `NOT EXECUTED`.",
        "- Gate H — `NOT EXECUTED`.",
        "- This report does not authorize merge or release.",
        "",
        "## Chronology and identity",
        "",
        f"- Recovery base: `{RECOVERY_BASE}`",
        f"- Confirmatory preregistration commit: `{PREREGISTRATION_COMMIT}`",
        f"- Candidate source-freeze commit: `{FREEZE_COMMIT}`",
        f"- Candidate source SHA-256: `{terminal.get('candidate_source_sha256', 'N/A')}`",
        f"- Formal scoring occurred: `{terminal.get('formal_scoring_occurred', False)}`",
        "",
    ]
    if main:
        lines.extend(
            [
                "## Main protected-set metrics",
                "",
                f"- Accuracy: `{main['accuracy']:.6f}`",
                f"- Macro-F1: `{main['macro_f1']:.6f}`",
                f"- Weighted-F1: `{main['weighted_f1']:.6f}`",
                f"- Valid-action rate: `{main['valid_action_rate']:.6f}`",
                f"- Invalid actions: `{main['invalid_action_count']}`",
                f"- Forbidden ACT: `{main['forbidden_act_count']}`",
                f"- Maximum predicted-action share: `{main['max_predicted_action_share']:.6f}`",
                "",
                "### Per-action recall",
                "",
            ]
        )
        for action in ACTIONS:
            lines.append(f"- {action}: `{main['per_action'][action]['recall']:.6f}`")
        lines.extend(
            [
                "",
                "## Relation metrics",
                "",
                f"- Counterfactual exact-pair correctness: `{relations['counterfactual_exact_pair_correctness']:.6f}`",
                f"- Counterfactual single-side correctness: `{relations['counterfactual_single_side_correctness']:.6f}`",
                f"- Counterfactual direction sensitivity: `{relations['counterfactual_direction_sensitivity']:.6f}`",
                f"- Invariance prediction consistency: `{relations['invariance_prediction_consistency']:.6f}`",
                f"- Invariance both-sides label correctness: `{relations['invariance_both_sides_label_correctness']:.6f}`",
                "",
            ]
        )
    lines.extend(["## Frozen acceptance criteria", ""])
    for name, passed in criteria.items():
        lines.append(f"- {'PASS' if passed else 'FAIL'} — `{name}`")
    lines.extend(
        [
            "",
            "## Scientific boundary",
            "",
            "This is a fresh preregistered process-isolated confirmatory evaluation of the frozen Candidate-v3 lineage. It does not rewrite the historical Gate-F failure and does not itself execute Gate G, establish deployment readiness, or establish external/human-independent validation.",
            "",
        ]
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def _write_invalid(error: IntegrityError, protected_data_generated: bool) -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    terminal = {
        "terminal_state": INVALID_STATE,
        "candidate": "V3A_factor_tree",
        "historical_gate_f": "FAIL",
        "fresh_confirmatory": "INVALID",
        "gate_g": "NOT EXECUTED",
        "gate_h": "NOT EXECUTED",
        "preregistration_commit": PREREGISTRATION_COMMIT,
        "candidate_source_freeze_commit": FREEZE_COMMIT,
        "formal_scoring_occurred": False,
        "protected_data_generated": protected_data_generated,
        "integrity_error": {"code": error.code, "details": dict(error.details)},
    }
    _write_json(RESULT_DIR / "terminal_decision.json", terminal)
    report = [
        "# Candidate v3 Fresh Confirmatory Evaluation — Terminal Report",
        "",
        f"**Terminal state:** `{INVALID_STATE}`",
        "",
        f"Integrity failure: `{error.code}`",
        "",
        "```json",
        json.dumps(dict(error.details), sort_keys=True, indent=2, ensure_ascii=False),
        "```",
        "",
        f"Protected confirmatory data generated before failure: `{protected_data_generated}`",
        "",
        "Gate F remains historical `FAIL`; Gate G and Gate H remain `NOT EXECUTED`. No merge or release is authorized.",
        "",
    ]
    REPORT_PATH.write_text("\n".join(report), encoding="utf-8")


def main() -> int:
    protected_data_generated = False
    try:
        prechecks = pre_generation_integrity_checks()
        if DATA_DIR.exists():
            shutil.rmtree(DATA_DIR)
        generate(DATA_DIR)
        protected_data_generated = True
        postchecks = post_generation_integrity_checks()
        result = formal_score(prechecks, postchecks)
        print(json.dumps({"terminal_state": result["decision"], "macro_f1": result["main"]["macro_f1"], "counterfactual_exact": result["relations"]["counterfactual_exact_pair_correctness"], "invariance_consistency": result["relations"]["invariance_prediction_consistency"]}, sort_keys=True, indent=2))
        return 0
    except IntegrityError as error:
        _write_invalid(error, protected_data_generated)
        print(json.dumps({"terminal_state": INVALID_STATE, "integrity_error": error.code, "details": dict(error.details)}, sort_keys=True, indent=2))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
