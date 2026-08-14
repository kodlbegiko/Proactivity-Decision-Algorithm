from __future__ import annotations

def blocked_report()->dict:
    return {"gate_decision":"GATE B — BLOCKED_BY_INDEPENDENT_ANNOTATION","raw_agreement":"NOT EXECUTED","cohen_kappa":"NOT EXECUTED","ambiguity":"NOT EXECUTED","domain_reliability":"NOT EXECUTED","counterfactual_reliability":"NOT EXECUTED","temporal_reliability":"NOT EXECUTED","post_label_leakage":"NOT EXECUTED","note":"Unmeasured human evidence is never represented as zero."}

def decide_gate_b(*,human_annotations_present:bool,raw_agreement:float|None=None,kappa:float|None=None,core_class_collapse:bool=False,label_leakage_acceptable:bool|None=None,all_other_conditions_pass:bool=False)->str:
    if not human_annotations_present:
        return "GATE B — BLOCKED_BY_INDEPENDENT_ANNOTATION"
    if raw_agreement is None or kappa is None or raw_agreement<0.80 or kappa<0.60:
        return "GATE B — FAIL_ANNOTATION_RELIABILITY"
    if core_class_collapse:
        return "GATE B — BLOCKED_CORE_CLASS_COLLAPSE"
    if label_leakage_acceptable is False:
        return "GATE B — FAIL_LEAKAGE"
    if label_leakage_acceptable is not True or not all_other_conditions_pass:
        return "GATE B — BLOCKED_BY_INDEPENDENT_ANNOTATION"
    return "GATE B — PASS"
