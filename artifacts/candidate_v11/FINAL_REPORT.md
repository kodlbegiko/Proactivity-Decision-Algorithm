# Candidate-v11 Post-V7R Clean Generalization Recovery — Final Development Report

## Terminal decision

`CANDIDATE_VNEXT DEVELOPMENT PASS — READY_FOR_INDEPENDENT_QUALIFICATION`

This is a development terminal state, **not** an independent qualification result.

## Lineage

- Lineage: `Candidate-v11`
- Selected candidate: `Candidate-v11B`
- Branch: `research/candidate-v11-post-v7r-semantic-generalization`
- V7R terminal ancestry commit: `a247c8b9685a48984d7ca9063ba7576d771edb54`
- Candidate/fresh-validation source freeze commit: `a59ea722d9d9c3b8bc83fc0a36e33f708c996b21`
- CI-tested head before this report-only commit: `12100d026e91f1c0a8e24732533830010f338534`
- V7R protected raw example access: `NONE`

Candidate-v8, v9, and v10 are preserved historical lineages. Candidate-v11 was created from the V7R terminal ancestry to avoid identifier collision and historical rewrite.

## Architecture

Selected architecture: **Semantic Evidence Graph + weighted evidence aggregation (Variant B)**.

Pipeline:

`text -> semantic units -> typed propositions -> structural polarity/scope/temporal representation -> evidence graph -> factor hypotheses -> calibrated uncertainty -> Protocol-v2 latent state -> frozen action policy`

Variant A failed semantic reconstruction and negation robustness. Variants B and C tied on recorded scientific metrics; the preregistered parsimony tie-break selected lower-complexity B.

## Development evidence

- Total development evidence: **6,050 examples**
- Development Fresh OOD Macro-F1: **0.9964178843**
- Exact latent-state reconstruction: **0.9947107438**
- Mean factor accuracy: **0.9995592287**
- ACT-critical factor accuracy: **1.0000000000**
- Critical UNKNOWN rate: **0.0000000000**
- ACT precision: **1.0000000000**
- ACT recall: **1.0000000000**

Development family Macro-F1:

- Lexical: **1.0000000000**
- Rendering: **1.0000000000**
- Compositional: **0.9943233704**
- Negation: **1.0000000000**
- Scope: **0.9891167589**
- Temporal: **1.0000000000**
- Mixed Adversarial: **0.9914978618**

## Fresh internal validation

Fresh validation used seed `5501`, bank offset `1`, and action-stratified sampling with 250 truth examples per action; total **1,500 examples**. No architecture mutation occurred after this validation began.

- Fresh OOD Macro-F1: **0.9986653200**
- Lexical Macro-F1: **1.0000000000**
- Rendering Macro-F1: **1.0000000000**
- Compositional Macro-F1: **0.9954946728**
- Negation Macro-F1: **1.0000000000**
- Scope Macro-F1: **1.0000000000**
- Temporal Macro-F1: **1.0000000000**
- Mixed Adversarial Macro-F1: **0.9947036570**
- Exact latent-state reconstruction: **0.9986666667**
- Mean factor accuracy: **0.9998888889**
- ACT-critical factor accuracy: **1.0000000000**
- Critical UNKNOWN rate: **0.0000000000**
- False UNKNOWN rate: **0.0000000000**
- Legitimate UNKNOWN recall: **1.0000000000**
- Counterfactual exact-pair: **1.0000000000**
- Invariance action consistency: **1.0000000000**
- ACT precision: **1.0000000000**
- ACT recall: **1.0000000000**
- Forbidden ACT: **0**
- Invalid action: **0**
- Catastrophic collapse: **FALSE**

## Validation-integrity history

Two previously exposed validation attempts were not selected as best runs; they were downgraded to development evidence as required:

1. Seed `3301`: zero ACT truth support made ACT recall non-estimable.
2. Seed `4409`: false UNKNOWN exceeded the preregistered Gate E limit.

The final fresh validation was generated only after architecture returned to development and was refrozen.

## Repository regression evidence

GitHub Actions run `31927121423`, job `95116322562`, on tested head `12100d026e91f1c0a8e24732533830010f338534`:

- Frozen V7R runtime materialization: **PASS**
- Deterministic repository fixture preparation: **PASS**
- Full repository `pytest -q`: **PASS**
- Candidate-v11 frozen development checks: **PASS**

Two infrastructure failures were preserved in `INFRASTRUCTURE_RETRY_001.json` and `INFRASTRUCTURE_RETRY_002.json`. Both were test-environment setup failures; neither changed candidate code, scientific parameters, seeds, thresholds, or validation results.

## Research integrity

- Research integrity: **PASS**
- V7R protected raw example access: **NONE**
- Candidate mutation after final validation: **FALSE**
- Historical lineage rewrite: **FALSE**
- Best-run cherry-picking: **FALSE**
- Selective scientific rerun: **FALSE**
- Qualification executed: **NO**

## Authorized next action

Run a **separately preregistered, independently isolated protected qualification** for frozen Candidate-v11B. It must not be performed by treating this development validation as protected evidence.
