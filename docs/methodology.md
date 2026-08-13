# Methodology v1 — Gate B Measurement Design

## Research design

This repository studies **intervention control**, not general agent task completion. Candidate development remains forbidden until Gate B is supported.

## Two input tracks

### Raw-context track — primary validity track

Policy-visible input is restricted to observable text/state facts: current activity, event summary, observable facts, recent history, permission evidence, time context, source kind, timestamp/domain, and candidate actions. It excludes researcher-derived scalar judgments such as `importance`, `urgency`, `expected_delay_cost`, `interruptibility`, and `action_risk`.

### Structured-state track — mechanistic control only

The original normalized scalar state is retained for controlled ablation/mechanistic analysis. It must not be presented as the only evidence of general intervention reasoning.

## Development v1

`development_v1.jsonl` contains 144 deterministic synthetic-but-realistic scenarios, 24 in each of six domains: study, work, scheduling, communication, device, and travel.

It includes 72 independent scenarios, 24 counterfactual pairs / 48 pair members, and 6 temporal mini-sequences / 24 sequence members. Pair/sequence design metadata is stored separately and is not policy-visible or annotator-visible.

## Dataset roles

- `pilot_v0.jsonl`: infrastructure-only; prohibited for formal policy ranking because it failed structural template leakage.
- `development_v1.jsonl`: Gate-B development candidate; formal baseline development remains blocked until independent annotation and full label-dependent leakage checks pass.
- protected set: not created yet.

## Ground truth

Scenario generation and annotation are separated. Dataset records contain no gold/preferred action. Independent humans supply preferred action, acceptable-action set, confidence, ambiguity, reason code, and criticality.

## First-pass evidence handling

Completed annotation files are validated against the frozen packet before analysis. Validation requires the complete 144-scenario set, legal annotation fields, and byte-equivalent source fields (`scenario_id`, domain, timestamp, scenario context). Source mutation or duplicate/missing scenarios fail closed.

Validated first-pass files can then be copied into an immutable raw archive. The archival workflow refuses overwrite, records SHA-256 in `annotations/raw/SHA256SUMS`, and writes a manifest without annotator identity. Adjudication must occur only after first-pass evidence is preserved and initial agreement is computed.

## Reliability workflow

**IMPLEMENTED / PIPELINE TESTABLE / HUMAN EXECUTION PENDING:**

- preferred-action raw agreement and Cohen's kappa;
- degenerate-kappa warning for constant-class collapse;
- six-class confusion matrix and per-class agreement;
- acceptable-action Jaccard and mutual acceptability as secondary evidence;
- ambiguity and confidence distributions;
- domain-specific reliability;
- explicit `IGNORE vs WAIT` and `ASK vs ACT` core-class diagnostics;
- disagreement categories using human reason codes;
- counterfactual transition consistency without hidden expected labels;
- temporal-sequence consistency without forcing monotonic escalation.

Primary thresholds remain raw agreement >= 0.80 and Cohen's kappa >= 0.60. There is no invented numeric threshold for core-class collapse; core distinctions are reported descriptively unless a threshold is frozen before results.

## Leakage and control workflow

Pre-annotation checks include exact duplicates, normalized structural duplicates, unrelated near duplicates, metadata/ID leakage, ordering/domain concentration, and design-family lexical diagnostics.

Post-label lexical and metadata analyses are implemented behind an explicit validated-human-label guard. Without such evidence they report `NOT_EXECUTED_NO_INDEPENDENT_LABELS`.

Measurement controls include row-order invariance after labels exist and pre-human pipeline checks for raw-context scalar removal, hidden-metadata separation, and deterministic context corruption. These controls test measurement infrastructure; they are not candidate-performance results.

## Evaluation principle

Metric denominators remain explicitly defined in `docs/metric_definitions.md`. Unsafe-autonomy rate conditions on predicted autonomous actions. The existing single-axis escalation order is retained only as a diagnostic convenience; pairwise interpretation is primary where permission and intervention intensity are not a clean single ordering.

## Gate order

Until all independent-human reliability and post-label leakage requirements pass, Gate B remains `BLOCKED_BY_INDEPENDENT_ANNOTATION`. No formal Gate C baseline leaderboard, candidate tuning, protected evaluation, merge, or release is authorized by this pre-human infrastructure work.
