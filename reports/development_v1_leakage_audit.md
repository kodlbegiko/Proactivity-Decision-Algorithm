# Development v1 Leakage Audit — Pre-Annotation

Date: 2026-08-13

## Executed result after deterministic-generator remediation

```text
scenario_count=144
unique_ids=144
domain_counts=24 each across 6 domains
exact_duplicate_members=0
structural_duplicate_members=0
unrelated_near_duplicate_pairs=0
intentional_related_near_pairs=4
metadata_leakage_findings=[]
longest_same_domain_run=3
pre_annotation_leakage_gate=PASS
label_dependent_lexical_audit=NOT_EXECUTED_NO_INDEPENDENT_LABELS
shuffled_feature_control=FRAMEWORK_PENDING_LABELS
```

## Interpretation

The replacement batch eliminates the known pilot-v0 repeated-template defect under the implemented exact, structured-state, unrelated-near-duplicate, metadata/ID, and ordering checks.

Four high-similarity pairs are intentionally related counterfactual/temporal cases and are linked only in hidden metadata.

The construction-family diagnostic can identify vocabulary shared by counterfactual and temporal examples. This is a **warning**, not a gold-label leakage result: no independent gold labels exist yet, and construction family is not an action label. The required post-annotation audit must test token associations against independent preferred actions and acceptable-action sets. If construction-family vocabulary predicts human labels beyond trivial controls, the affected scenarios must be revised before Gate B can pass.

## Gate status

This is only a **pre-annotation** leakage pass. Gate B cannot pass until label-dependent lexical analysis and shuffled/corrupted-feature controls are executed on immutable independent labels.
