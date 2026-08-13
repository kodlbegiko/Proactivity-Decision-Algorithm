# PROACTIVITY DECISION ALGORITHM — GATE B EXECUTION REPORT

Date: 2026-08-13

## Repository target

- Branch: `research/proactivity-decision-v0`
- PR: #1 (Draft; do not merge)
- Gate-B execution started from `e8cbb8f76e14079bc8b458b12cf93b51454f5c15`.

## What was executed

- systematic 2026 primary-source novelty comparison;
- schema feature-leakage review and raw-context primary projection;
- diversified 144-scenario development-v1 generation;
- 24 counterfactual pairs and six temporal mini-sequences with hidden metadata separated;
- pre-annotation leakage suite;
- blinded annotation packet generation;
- annotation parser, agreement/disagreement tooling, and metric operationalization;
- unsafe-autonomy denominator bug discovery and correction;
- local tests, dataset validation, hash validation, and leakage audit;
- remote CI artifact-transport failure diagnosis and deterministic-generator remediation.

## Novelty verdict

`PARTIAL NOVELTY ONLY`

Broad first claims over intervention timing, silence, permission/consent, ask-or-act, and non-intrusive assistance are not supported. The remaining research question is whether the integrated six-level cross-domain intervention-control formulation and asymmetric failure taxonomy are independently measurable and useful.

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
intentional_related_near_pairs=4
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

## Local validation after CI remediation

```text
generated=144 domains=6
SHA-256: 4/4 generated artifacts OK
pytest: 10 passed
VALID: 144 scenarios; unique_ids=144
pre_annotation_leakage_gate=PASS
```

## Research-integrity incidents / negative findings

- pilot_v0 structural leakage FAIL remains preserved;
- broad novelty claim collapsed to `PARTIAL NOVELTY ONLY` after KnowU-Bench/PACT/NIABench and related work;
- unsafe-autonomy denominator bug was found before metric freeze and corrected;
- GitHub Actions run `31701084246` failed because connector-transported gzip data was corrupt; the binary transport path was removed instead of retrying until green;
- label-dependent lexical leakage and human agreement remain unexecuted.

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

Run `python scripts/generate_development_v1.py`, verify `sha256sum -c data/development/development_v1.sha256`, then obtain two genuinely independent blinded first-pass annotations using `annotation/instructions_v1.md`, `annotation/packet_a.csv`, and `annotation/packet_b.csv`. Hash the returned files before any discussion, calculate raw agreement/kappa, then run disagreement, label-conditional lexical, and shuffled/corrupted-feature controls.
