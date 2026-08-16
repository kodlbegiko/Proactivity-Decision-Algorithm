from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

from proactivity.benchmark_v2 import (
    ACTIONS, CONFIG_PATH, DOMAINS, FIELD_ORDER, FORBIDDEN_CANDIDATE_FIELDS,
    ORACLE_PATH, ROOT, SPEC_PATH, artifact_texts, build_benchmark, build_manifest,
    canonical_json, frozen_integrity, load_config, sha256_file, state_key, tokenize,
)
from proactivity.specification import evaluate, load_spec, spec_sha256


def majority_accuracy(rows: Iterable[tuple[str, str]]) -> float:
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    total = 0
    for feature, action in rows:
        groups[feature][action] += 1
        total += 1
    if total == 0:
        return 0.0
    return sum(max(counts.values()) for counts in groups.values()) / total


def exact_state_differences(a: Mapping[str, Any], b: Mapping[str, Any]) -> dict[str, list[Any]]:
    return {field: [a[field], b[field]] for field in FIELD_ORDER if a[field] != b[field]}


def build_report() -> dict[str, Any]:
    config = load_config()
    criteria = config["preregistered_criteria"]
    integrity = frozen_integrity()
    bundle1 = build_benchmark()
    bundle2 = build_benchmark()
    texts1 = artifact_texts(bundle1)
    texts2 = artifact_texts(bundle2)
    manifest = build_manifest(bundle1, texts1)
    reproducible = texts1 == texts2 and build_manifest(bundle1, texts1) == build_manifest(bundle2, texts2)

    candidate = bundle1["candidate"]
    private = bundle1["private"]
    relations = bundle1["relations"]
    exhaustive = bundle1["exhaustive"]
    candidate_by_id = {row["scenario_id"]: row for row in candidate}
    private_by_id = {row["scenario_id"]: row for row in private}

    duplicate_ids = len(private) - len(private_by_id)
    exact_candidate_counter = Counter(canonical_json({"domain":r["domain"],"observation":r["observation"]}) for r in candidate)
    exact_duplicate_candidate_records = sum(count - 1 for count in exact_candidate_counter.values() if count > 1)
    state_counter = Counter(state_key(row["state"]) for row in private)
    structural_duplicate_members = sum(count - 1 for count in state_counter.values() if count > 1)

    forbidden_metadata_findings: list[dict[str, Any]] = []
    direct_answer_tokens: list[dict[str, str]] = []
    action_word = re.compile(r"\b(ignore|wait|suggest|notify|ask|act)\b", re.I)
    for row in candidate:
        exposed = sorted(set(row) & FORBIDDEN_CANDIDATE_FIELDS)
        if exposed:
            forbidden_metadata_findings.append({"scenario_id":row["scenario_id"],"fields":exposed})
        hits = sorted(set(match.group(1).upper() for match in action_word.finditer(row["observation"])))
        if hits:
            direct_answer_tokens.append({"scenario_id":row["scenario_id"],"tokens":",".join(hits)})

    manual_gold_fields = {"expected_action","preferred_action","gold","gold_action","answer_override","manual_action"}
    manual_gold_findings = [
        {"scenario_id": row["scenario_id"], "fields": sorted(set(row) & manual_gold_fields)}
        for row in private if set(row) & manual_gold_fields
    ]
    source_text = (ROOT / "src" / "proactivity" / "benchmark_v2.py").read_text(encoding="utf-8") + (ROOT / "scripts" / "generate_benchmark_v2.py").read_text(encoding="utf-8")
    llm_markers = [marker for marker in ("openai", "anthropic", "ollama", "litellm", "requests.post", "httpx") if marker in source_text.lower()]

    oracle_mismatches: list[dict[str, Any]] = []
    for row in private:
        result = evaluate(row["state"], spec_path=SPEC_PATH)
        if result.status != "VALID_DECISION" or result.action != row["oracle_action"] or result.matched_rule != row["matched_rule"] or list(result.prohibition_rules) != row["prohibition_rules"]:
            oracle_mismatches.append({"scenario_id":row["scenario_id"],"stored_action":row["oracle_action"],"recomputed_action":result.action,"stored_rule":row["matched_rule"],"recomputed_rule":result.matched_rule})

    action_counts = Counter(row["oracle_action"] for row in private)
    exhaustive_action_counts = Counter(row.action for row in exhaustive)
    benchmark_rule_counts = Counter(row["matched_rule"] for row in private)
    exhaustive_selected_rule_counts = Counter(row.matched_rule for row in exhaustive)
    spec = load_spec(SPEC_PATH)
    rule_coverage: dict[str, Any] = {}
    for rule in spec["selection_rules"]:
        rid = rule["id"]
        selected_reachable = exhaustive_selected_rule_counts[rid]
        bench = benchmark_rule_counts[rid]
        if rid == "R_FALLBACK_IGNORE" and selected_reachable == 0:
            status = "SHADOWED_NONSELECTED_FALLBACK"
        elif selected_reachable > 0 and bench >= int(criteria["minimum_examples_per_selected_nonfallback_rule"]):
            status = "COVERED"
        elif selected_reachable > 0:
            status = "COVERAGE_GAP"
        else:
            status = "UNREACHABLE_AS_SELECTED"
        rule_coverage[rid] = {"reachable_selected_state_count":selected_reachable,"benchmark_example_count":bench,"action":rule["action"],"coverage_status":status}

    prohibition_counts = Counter(pid for row in private for pid in row["prohibition_rules"])
    prohibition_safety_violations: list[dict[str, Any]] = []
    prohibition_coverage: dict[str, Any] = {}
    for prohibition in spec.get("hard_prohibitions", []):
        pid = prohibition["id"]
        prohibited_actions = set(prohibition["actions"])
        for row in private:
            if pid in row["prohibition_rules"] and row["oracle_action"] in prohibited_actions:
                prohibition_safety_violations.append({"scenario_id":row["scenario_id"],"prohibition_id":pid,"action":row["oracle_action"]})
        rel_count = sum(1 for rel in relations if rel["kind"] == "prohibition_counterfactual" and rel["prohibition_id"] == pid)
        prohibition_coverage[pid] = {"benchmark_trigger_count":prohibition_counts[pid],"prohibited_actions":sorted(prohibited_actions),"counterfactual_pair_count":rel_count}

    relation_violations: list[dict[str, Any]] = []
    counterfactual_families = 0
    prohibition_counterfactual_families = 0
    temporal_sequences = 0
    for rel in relations:
        ids = rel["scenario_ids"]
        rows = [private_by_id[sid] for sid in ids]
        if len({row["domain"] for row in rows}) != 1 or len({row["template_family"] for row in rows}) != 1:
            relation_violations.append({"id":rel["id"],"reason":"domain_or_template_changed_within_relation"})
        if rel["kind"] in {"counterfactual","prohibition_counterfactual"}:
            diffs = exact_state_differences(rows[0]["state"], rows[1]["state"])
            if list(diffs) != [rel["changed_field"]] or rows[0]["oracle_action"] == rows[1]["oracle_action"]:
                relation_violations.append({"id":rel["id"],"reason":"invalid_single-variable_action-changing_pair","diffs":diffs})
            if rel["kind"] == "counterfactual":
                counterfactual_families += 1
            else:
                prohibition_counterfactual_families += 1
                pid = rel["prohibition_id"]
                trig = [pid in row["prohibition_rules"] for row in rows]
                if trig[0] == trig[1]:
                    relation_violations.append({"id":rel["id"],"reason":"prohibition_trigger_did_not_toggle"})
        elif rel["kind"] == "temporal":
            temporal_sequences += 1
            expected_deltas = rel["deltas"]
            actual_deltas = [exact_state_differences(a["state"], b["state"]) for a,b in zip(rows,rows[1:])]
            if actual_deltas != expected_deltas:
                relation_violations.append({"id":rel["id"],"reason":"temporal_delta_mismatch","expected":expected_deltas,"actual":actual_deltas})
            if [row["temporal_step"] for row in rows] != list(range(len(rows))):
                relation_violations.append({"id":rel["id"],"reason":"temporal_step_corruption"})

    counterfactual_violations = [v for v in relation_violations if v["id"].startswith("cf-")]
    temporal_violations = [v for v in relation_violations if v["id"].startswith("ts-")]
    prohibition_cf_violations = [v for v in relation_violations if v["id"].startswith("pcf-")]

    split_sets: dict[str, set[str]] = defaultdict(set)
    for row in private:
        group = row["relation_group"] or row["state_family_id"]
        split_sets[group].add(row["split"])
    split_family_leakage = {group:sorted(values) for group,values in split_sets.items() if len(values) > 1}
    split_counts = Counter(row["split"] for row in private)

    template_counts = Counter(row["template_family"] for row in private)
    largest_template_share = max(template_counts.values(), default=0) / max(len(private), 1)
    domain_counts = Counter(row["domain"] for row in private)
    domain_action = {domain:dict(sorted(Counter(row["oracle_action"] for row in private if row["domain"] == domain).items())) for domain in DOMAINS}

    # Diagnostics only: these are not Gate-D formal baselines.
    domain_only_accuracy = majority_accuracy((row["domain"],row["oracle_action"]) for row in private)
    template_only_accuracy = majority_accuracy((row["template_family"],row["oracle_action"]) for row in private)
    id_prefix_accuracy = majority_accuracy((row["scenario_id"][4:5],row["oracle_action"]) for row in private)
    row_bucket_accuracy = majority_accuracy((str(index % 10),row["oracle_action"]) for index,row in enumerate(private))

    token_actions: dict[str, Counter[str]] = defaultdict(Counter)
    token_freq: Counter[str] = Counter()
    for c_row in candidate:
        action = private_by_id[c_row["scenario_id"]]["oracle_action"]
        for token in set(tokenize(c_row["observation"])):
            token_freq[token] += 1
            token_actions[token][action] += 1
    high_purity_tokens: list[dict[str, Any]] = []
    for token,count in token_freq.items():
        if count < 5:
            continue
        purity = max(token_actions[token].values()) / count
        if purity >= 0.95:
            classification = "FORBIDDEN_ANSWER_LEAK" if token.upper() in ACTIONS else "POSSIBLE_GENERATOR_SHORTCUT"
            high_purity_tokens.append({"token":token,"count":count,"purity":round(purity,6),"classification":classification})
    high_purity_tokens.sort(key=lambda item:(-item["purity"],-item["count"],item["token"]))
    lexical_forbidden = [item for item in high_purity_tokens if item["classification"] == "FORBIDDEN_ANSWER_LEAK"]

    candidate_fields = set().union(*(row.keys() for row in candidate)) if candidate else set()
    private_sensitive = {"state","oracle_action","matched_rule","prohibition_rules","template_family","state_family_id","relation_group","counterfactual_family_id","prohibition_counterfactual_id","temporal_sequence_id","temporal_step","split"}
    candidate_private_forbidden_overlap = sorted(candidate_fields & private_sensitive)

    criteria_failures: list[str] = []
    if not integrity["spec_match"] or not integrity["oracle_match"]:
        criteria_failures.append("UPSTREAM_INTEGRITY_MISMATCH")
    if not reproducible:
        criteria_failures.append("NONDETERMINISTIC_REGENERATION")
    checks = [
        (len(manual_gold_findings) <= criteria["manual_gold_findings_max"], "MANUAL_GOLD_FOUND"),
        (len(llm_markers) <= criteria["llm_gold_findings_max"], "LLM_GOLD_DEPENDENCY_FOUND"),
        (len(oracle_mismatches) <= criteria["oracle_mismatch_findings_max"], "ORACLE_MISMATCH"),
        (len(forbidden_metadata_findings) + len(direct_answer_tokens) <= criteria["forbidden_candidate_metadata_max"], "FORBIDDEN_CANDIDATE_METADATA"),
        (exact_duplicate_candidate_records <= criteria["exact_duplicate_candidate_records_max"], "EXACT_CANDIDATE_DUPLICATES"),
        (structural_duplicate_members <= criteria["accidental_structural_duplicate_members_max"], "STRUCTURAL_DUPLICATES"),
        (len(split_family_leakage) <= criteria["split_family_leakage_max"], "SPLIT_FAMILY_LEAKAGE"),
        (counterfactual_families >= criteria["minimum_counterfactual_families"], "COUNTERFACTUAL_COVERAGE_GAP"),
        (temporal_sequences >= criteria["minimum_temporal_sequences"], "TEMPORAL_COVERAGE_GAP"),
        (len(counterfactual_violations) <= criteria["counterfactual_relation_violations_max"], "COUNTERFACTUAL_RELATION_VIOLATION"),
        (len(temporal_violations) <= criteria["temporal_relation_violations_max"], "TEMPORAL_RELATION_VIOLATION"),
        (largest_template_share <= criteria["largest_observation_template_family_share_max"], "TEMPLATE_DOMINANCE"),
        (len(candidate_private_forbidden_overlap) <= criteria["candidate_private_forbidden_field_overlap_max"], "CANDIDATE_PRIVATE_SCHEMA_OVERLAP"),
        (duplicate_ids == 0, "DUPLICATE_SCENARIO_ID"),
        (not prohibition_safety_violations, "HARD_PROHIBITION_VIOLATION"),
        (not prohibition_cf_violations, "PROHIBITION_COUNTERFACTUAL_VIOLATION"),
        (not lexical_forbidden, "LEXICAL_ANSWER_LEAK"),
        (all(domain_counts[d] > 0 for d in DOMAINS), "DOMAIN_COVERAGE_GAP"),
        (all(split_counts[s] > 0 for s in ("development","validation","protected_test")), "SPLIT_EMPTY"),
    ]
    for ok, reason in checks:
        if not ok:
            criteria_failures.append(reason)
    for action in ACTIONS:
        if action_counts[action] < criteria["minimum_examples_per_action"]:
            criteria_failures.append("ACTION_COVERAGE_GAP:" + action)
    for rid,item in rule_coverage.items():
        if item["reachable_selected_state_count"] > 0 and rid != "R_FALLBACK_IGNORE" and item["benchmark_example_count"] < criteria["minimum_examples_per_selected_nonfallback_rule"]:
            criteria_failures.append("RULE_COVERAGE_GAP:" + rid)
    for pid,item in prohibition_coverage.items():
        if item["benchmark_trigger_count"] < criteria["minimum_examples_per_hard_prohibition"]:
            criteria_failures.append("PROHIBITION_COVERAGE_GAP:" + pid)
        if item["counterfactual_pair_count"] < 1:
            criteria_failures.append("PROHIBITION_RELATION_GAP:" + pid)

    criteria_failures = sorted(set(criteria_failures))
    if any(item.startswith("UPSTREAM_") for item in criteria_failures):
        verdict = "GATE C — BLOCKED: UPSTREAM_INTEGRITY_MISMATCH"
    elif criteria_failures:
        verdict = "GATE C — FAIL: BENCHMARK_VALIDITY_CRITERIA_NOT_MET"
    else:
        verdict = "GATE C — PASS"

    return {
        "protocol":"PDA Protocol v2","gate":"C",
        "spec_sha256":spec_sha256(SPEC_PATH),"oracle_hash":sha256_file(ORACLE_PATH),
        "benchmark_version":config["benchmark_version"],"benchmark_sha256":manifest["artifact_sha256"],
        "scenario_count":len(private),"unique_ids":len(private_by_id),
        "upstream_integrity":integrity,
        "ground_truth_provenance":{"oracle_derived_records":len(private)-len(oracle_mismatches),"manual_gold_findings":len(manual_gold_findings),"llm_gold_findings":len(llm_markers),"oracle_mismatch_findings":len(oracle_mismatches),"manual_gold_details":manual_gold_findings,"llm_markers":llm_markers},
        "representation":{"candidate_visible_fields":sorted(candidate_fields),"private_forbidden_overlap":candidate_private_forbidden_overlap,"direct_answer_token_findings":direct_answer_tokens,"track_a":"structured state without oracle-private labels","track_b":"deterministically generated semantic observation/context"},
        "diversity":{"exact_duplicate_candidate_records":exact_duplicate_candidate_records,"structural_duplicate_members":structural_duplicate_members,"template_distribution":dict(sorted(template_counts.items())),"largest_template_family_share":largest_template_share,"domain_distribution":dict(sorted(domain_counts.items())),"domain_action_distribution":domain_action},
        "action_coverage":dict(sorted(action_counts.items())),"natural_exhaustive_action_distribution":dict(sorted(exhaustive_action_counts.items())),
        "rule_coverage":rule_coverage,"prohibition_coverage":prohibition_coverage,"prohibition_safety_violations":prohibition_safety_violations,
        "counterfactual":{"family_count":counterfactual_families,"prohibition_family_count":prohibition_counterfactual_families,"violations":counterfactual_violations + prohibition_cf_violations},
        "temporal":{"sequence_count":temporal_sequences,"violations":temporal_violations},
        "split_integrity":{"counts":dict(sorted(split_counts.items())),"group_leakage":split_family_leakage,"public_holdout_limitation":"The protected_test split is a deterministic public freeze, not independent Gate-F protected evidence."},
        "leakage":{"forbidden_metadata_findings":forbidden_metadata_findings,"identifier":{"id_prefix_diagnostic_accuracy":id_prefix_accuracy},"row":{"row_bucket_diagnostic_accuracy":row_bucket_accuracy},"domain":{"domain_only_diagnostic_accuracy":domain_only_accuracy},"template":{"template_only_diagnostic_accuracy":template_only_accuracy},"lexical":{"high_purity_tokens":high_purity_tokens[:100],"forbidden_answer_leaks":lexical_forbidden}},
        "reproducibility":{"deterministic_regeneration":reproducible,"artifact_sha256":manifest["artifact_sha256"]},
        "preregistered_criteria":criteria,"criteria_failures":criteria_failures,"gate_verdict":verdict,
        "claim_boundary":config["claim_boundary"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "reports" / "gate_c_report.json")
    args = parser.parse_args()
    report = build_report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"gate_verdict":report["gate_verdict"],"scenario_count":report["scenario_count"],"criteria_failures":report["criteria_failures"],"benchmark_sha256":report["benchmark_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
