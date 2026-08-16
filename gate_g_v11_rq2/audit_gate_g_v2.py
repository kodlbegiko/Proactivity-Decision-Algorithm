from __future__ import annotations

import inspect
from collections import Counter

from . import generator as generator_module
from . import protocol_oracle as oracle_module
from .generator import DOCKET_PREFIX, SUITE_CONFIG, TOTAL_CASES, EvaluationCase, dataset_sha256
from .metrics import ACTIONS, macro_f1
from .protocol_oracle import FACTOR_NAMES, validate_state

FORBIDDEN_GENERATOR_IMPORT_TOKENS=("benchmark_v11.generator","gate_g_v11","protected","candidate_v11")
FORBIDDEN_ORACLE_IMPORT_TOKENS=("candidate_v11","benchmark_v11","gate_g_v11")

def _source_has_forbidden_import(source,token):
    lower=source.lower();target=token.lower();return f"import {target}" in lower or f"from {target}" in lower

def _independent_action_metrics(cases,predictions):
    gold=[c.gold_action for c in cases];pred=[str(p.action) for p in predictions];return {"overall_accuracy":sum(g==p for g,p in zip(gold,pred))/len(cases),"overall_macro_f1":macro_f1(gold,pred,ACTIONS)}

def _independent_exact_state(cases,predictions):return sum(all(dict(p.factors).get(f)==c.gold_state[f] for f in FACTOR_NAMES) for c,p in zip(cases,predictions))/len(cases)

def audit_evaluation(cases,run_a,run_b,aggregate,expected_dataset_sha):
    checks={};checks["total_count"]=len(cases)==TOTAL_CASES;observed=Counter(c.suite for c in cases);checks["suite_counts"]=all(observed[s]==cfg["count"] for s,cfg in SUITE_CONFIG.items());checks["unique_case_ids"]=len({c.case_id for c in cases})==len(cases);checks["unique_prompts"]=len({c.prompt for c in cases})==len(cases);checks["fresh_namespace"]=all(c.prompt.startswith(DOCKET_PREFIX) for c in cases);checks["dataset_hash"]=dataset_sha256(cases)==expected_dataset_sha;checks["prediction_coverage"]=len(run_a)==len(run_b)==len(cases)
    def canonical(p):return (str(p.action),tuple(sorted(dict(p.factors).items())),tuple(sorted(dict(p.belief_resolution).items())),bool(p.contradiction_detected),bool(p.invalid_state))
    checks["determinism"]=all(canonical(a)==canonical(b) for a,b in zip(run_a,run_b));checks["gold_states_valid"]=all(validate_state(c.gold_state)[0] for c in cases);checks["gold_actions_valid"]=all(c.gold_action in ACTIONS for c in cases)
    g6=[c for c in cases if c.suite=="G6"];checks["g6_composition"]=sum(c.metadata.get("contradiction_case") is True for c in g6)==700 and sum(c.metadata.get("contradiction_case") is False for c in g6)==140;g14=[c for c in cases if c.suite=="G14"];checks["g14_pairs"]=len({c.metadata.get("pair_id") for c in g14})==600;g16=[c for c in cases if c.suite=="G16"];checks["g16_balance"]=Counter(c.gold_action for c in g16)==Counter({a:200 for a in ACTIONS})
    gs=inspect.getsource(generator_module);osrc=inspect.getsource(oracle_module);checks["generator_import_isolation"]=not any(_source_has_forbidden_import(gs,t) for t in FORBIDDEN_GENERATOR_IMPORT_TOKENS);checks["oracle_import_isolation"]=not any(_source_has_forbidden_import(osrc,t) for t in FORBIDDEN_ORACLE_IMPORT_TOKENS)
    independent=_independent_action_metrics(cases,run_a);independent["exact_structured_state_accuracy"]=_independent_exact_state(cases,run_a);checks["independent_metric_recompute"]=abs(independent["overall_accuracy"]-float(aggregate["overall_accuracy"]))<1e-12 and abs(independent["overall_macro_f1"]-float(aggregate["overall_macro_f1"]))<1e-12 and abs(independent["exact_structured_state_accuracy"]-float(aggregate["exact_structured_state_accuracy"]))<1e-12;checks["suite_completeness"]=set(aggregate["suite_metrics"])==set(SUITE_CONFIG)
    return {"audit_version":"GG-V11-RQ2-independent-auditor-v1","checks":checks,"independent_recomputed_metrics":independent,"pass":all(checks.values()),"previous_gate_g_used_as_scientific_evidence":False,"information_isolation_asserted":True}
