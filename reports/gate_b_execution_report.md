# PROACTIVITY DECISION ALGORITHM — GATE B EXECUTION REPORT

Date: 2026-08-13

## Repository target

- Branch: `research/proactivity-decision-v0`
- PR: #1 (must remain Draft)
- Base at start of this execution: `e8cbb8f76e14079bc8b458b12cf93b51454f5c15`

## What was executed

- systematic 2026 primary-source novelty comparison;
- schema feature-leakage review;
- raw-context primary projection implemented;
- 144-scenario diversified development-v1 generated;
- 24 counterfactual pairs and six temporal mini-sequences generated with hidden metadata separated;
- full pre-annotation leakage suite executed;
- blinded human annotation packets A/B generated;
- annotation parser, agreement and disagreement tooling implemented;
- operational metric definitions implemented and tested;
- unsafe-autonomy denominator bug found and corrected;
- local dataset validation and tests executed.

## Novelty verdict

`PARTIAL NOVELTY ONLY`

Broad first claims over intervention timing, silence, permission/consent, ask-or-act, and non-intrusive assistance are not supported by the current literature. The remaining research question is whether the integrated six-level cross-domain intervention-control formulation and asymmetric failure taxonomy are independently measurable and useful.

## Benchmark evidence

- pilot_v0: infrastructure only; prior structural leakage FAIL preserved.
- development_v1: 144 scenarios.
- domains: six, 24 each.
- counterfactual pairs: 24 (48 members).
- temporal sequences: six (24 members).

## Leakage evidence

```text
exact_duplicate_members=0
structural_duplicate_members=0
unrelated_near_duplicate_pairs=0
metadata_leakage_findings=[]
longest_same_domain_run=3
pre_annotation_leakage_gate=PASS
label_dependent_lexical_audit=NOT_EXECUTED_NO_INDEPENDENT_LABELS
shuffled_feature_control=FRAMEWORK_PENDING_LABELS
```

## Annotation evidence

```text
Independent annotators: NOT EXECUTED
Raw agreement: NOT EXECUTED
Cohen kappa: NOT EXECUTED
Ambiguous rate: NOT EXECUTED
```

## Local tests

```text
10 passed
VALID: 144 scenarios; unique_ids=144
```

## Gate decision

```text
Gate A: PASS (narrowed)
Gate B: BLOCKED_BY_INDEPENDENT_ANNOTATION
Gate C: BLOCKED BY GATE ORDER
Gate D: BLOCKED BY GATE ORDER
Gate E: BLOCKED BY GATE ORDER
Gate F: BLOCKED BY GATE ORDER
Gate G: BLOCKED BY GATE ORDER
Gate H: BLOCKED BY GATE ORDER
```

Evidence-weighted completion before independent labels: **25%**.

## Exact next action

Obtain two genuinely independent blinded first-pass annotations using:

- `annotation/instructions_v1.md`
- `annotation/packet_a.csv.gz` → decompress to `annotation/packet_a.csv`
- `annotation/packet_b.csv.gz` → decompress to `annotation/packet_b.csv`

Hash the returned files, calculate raw agreement/kappa, run disagreement analysis, label-conditional lexical audit, and shuffled/corrupted-feature controls. Gate B may pass only after those results satisfy the preregistered requirements.
