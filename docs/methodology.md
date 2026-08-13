# Methodology v1 — Gate B Measurement Design

## Research design

This repository studies **intervention control**, not general agent task completion. Candidate development remains forbidden until Gate B is supported.

## Two input tracks

### Raw-context track — primary validity track

Policy-visible input is restricted to observable text/state facts: current activity, event summary, observable facts, recent history, permission evidence, time context, source kind, timestamp/domain, and candidate actions. It excludes researcher-derived scalar judgments such as `importance`, `urgency`, `expected_delay_cost`, `interruptibility`, and `action_risk`.

This track is the primary benchmark track because directly providing those scalars may pre-compute much of the decision for the policy.

### Structured-state track — mechanistic control only

The original normalized scalar state is retained for controlled ablation/mechanistic analysis. It must not be presented as the only evidence of general intervention reasoning.

## Development v1

`development_v1.jsonl` contains 144 deterministic synthetic-but-realistic scenarios, 24 in each of six domains: study, work, scheduling, communication, device, and travel.

It includes:

- 72 domain-specific independent scenarios;
- 24 counterfactual pairs / 48 pair members;
- 6 temporal mini-sequences / 24 sequence members.

Pair/sequence design metadata is stored separately in `development_v1.meta.jsonl` and is not policy-visible or annotator-visible.

## Dataset roles

- `pilot_v0.jsonl`: infrastructure-only; prohibited for formal policy ranking because it failed structural template leakage.
- `development_v1.jsonl`: Gate-B development candidate; may be used for formal baseline development only after independent annotation and full label-dependent leakage checks pass.
- protected set: not created yet.

## Ground truth

Scenario generation and annotation are separated. Dataset records contain no gold/preferred action. Independent humans supply preferred action, acceptable-action set, confidence, ambiguity, reason code, and criticality.

## Leakage gates

Pre-annotation checks include exact duplicates, normalized structured duplicates, unrelated near duplicates, metadata/ID leakage, ordering/domain concentration, and hidden design-category lexical diagnostics.

After labels exist, label-dependent token shortcuts and shuffled/corrupted-feature controls must run before Gate B can pass.

## Agreement gate

First-pass independent preferred-action labels must achieve:

- raw agreement >= 0.80;
- Cohen's kappa >= 0.60 for two annotators (or preregistered appropriate multi-rater metric).

If either fails, no candidate tuning is allowed.

## Evaluation principle

All metric denominators are explicitly defined in `docs/metric_definitions.md`. Utility weights remain provisional and require sensitivity analysis; they cannot be tuned to favor a candidate.
