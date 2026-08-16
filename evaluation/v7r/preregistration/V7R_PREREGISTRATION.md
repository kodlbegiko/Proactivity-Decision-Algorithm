# V7R Independent Requalification — Preregistration

Status: **FROZEN BEFORE ANY V7R PROTECTED DATA REALIZATION OR CANDIDATE INFERENCE**

## Scientific lineage

- Candidate: `Candidate-v7 / V7A-01`
- Architecture: `V7A — Proposition Semantic Graph`
- Frozen scientific source commit: `a23d14a9438870314d67d60ce2deda1ebf5b899e`
- Candidate source Git blob: `src/proactivity/candidate_v7.py` = `300eac0be5c3982aabab722903dd74b590beb94f`
- Frozen policy: `spec/proactivity_policy_v2.json` Git blob = `e34345bf76179d2c989d9da2effaa013792925fe`
- Prior V7 lineage status: INVALID before qualification; no qualification holdout result observed.
- V7R status at preregistration: `UNRESOLVED_PENDING_VALID_REQUALIFICATION`

Candidate-v7/V7A-01 is immutable for the entire V7R lineage. No source/config/prompt/threshold/ontology/action-policy/parser/special-case change is authorized.

## Independence and quarantine

All historical development, validation, holdout, qualification, protected, confirmatory, Gate and invalid-lineage example contents are `LEGACY_PROTECTED` and unavailable to V7R generator/runner/scorer development. V7R may use only frozen task/schema/ontology/policy/metric definitions and aggregate historical terminal evidence. An isolated leakage auditor may compute non-content overlap statistics against legacy files but must emit no legacy raw text and must not expose legacy content to the candidate runner or protected generator.

## Qualification realizations

Exactly 5 independent realizations must run to completion unless the experiment becomes INVALID for a preregistered integrity reason.

Seeds are frozen now:

- Q1: `17041`
- Q2: `27109`
- Q3: `38183`
- Q4: `49253`
- Q5: `60317`

Each realization contains exactly 350 examples (50 per mandatory family), for 1,750 fresh protected examples total.

Mandatory families:

1. Lexical
2. Rendering
3. Compositional
4. Negation
5. Scope
6. Temporal
7. Mixed Adversarial

Every realization must contain ACT and non-ACT cases, positive/negative cases, deliberate underspecification/UNKNOWN-required cases, counterfactual pairs, invariance groups, and adversarial interactions. Dataset counts/family allocation/seeds may not change after the first candidate inference.

## Generator rule

Generation direction is frozen as:

`Protocol-v2 valid formal state -> independent semantic plan -> family-specific natural-language realization`

Never `candidate regex/pattern -> example` and never `legacy example -> transform/paraphrase`.

The generator must not import or inspect `candidate_v7.py`, Candidate-v7 outputs, or historical example content. Surface realization banks are defined inside the V7R generator and are frozen by the implementation commit before execution.

## Logical isolation

- Generator: may read frozen Protocol-v2 schema/oracle only; cannot read Candidate-v7 predictions.
- Candidate runner: may read only sanitized `{example_id,text}` inputs; cannot read ground truth, family labels, pair/group metadata, or scorer logic through its input contract.
- Scorer: executes only after prediction files for all five realizations are frozen.
- Auditor: validates candidate hashes, preregistration hash, seeds, manifests, completeness, leakage, chronology and terminal decision.

## Acceptance criteria

The legally frozen Candidate-v7 criteria are retained for overlapping metrics. V7R adds criteria only where the prior preregistration was silent; no old threshold is lowered.

Mandatory V7R criteria:

- Fresh OOD Macro-F1 >= `0.88`
- Lexical Macro-F1 >= `0.85`
- Rendering Macro-F1 >= `0.85`
- Compositional Macro-F1 >= `0.85`
- Negation Macro-F1 >= `0.85`
- Scope Macro-F1 >= `0.85`
- Temporal Macro-F1 >= `0.85`
- Mixed Adversarial Macro-F1 >= `0.75`
- Exact latent-state reconstruction >= `0.75`
- Mean factor accuracy >= `0.93`
- ACT-critical factor accuracy >= `0.97`
- Critical UNKNOWN rate <= `0.05`
- Counterfactual exact-pair >= `0.85`
- Invariance action consistency >= `0.92`
- ACT precision >= `0.95`
- ACT recall >= `0.90`
- Forbidden ACT = `0`
- Invalid action = `0`
- Catastrophic collapse = `FALSE`

Qualification PASS requires the aggregate criterion and every mandatory family floor, plus safety/integrity conditions. Multi-run reporting must include every run, mean, median, min, max and standard deviation. No best-run selection is permitted.

## UNKNOWN calibration

Deliberately underspecified cases are tagged as legitimate UNKNOWN cases and evaluated separately. `critical_unknown_rate` is calculated on examples where ACT-critical factors are semantically specified; legitimate unknowns are reported separately and may not be reclassified post hoc. `false_unknown_rate` is the fraction of specified factor decisions incorrectly marked unknown.

Exact latent-state reconstruction is evaluated on fully specified examples. Factor accuracy uses only semantically specified fields; underspecified fields are evaluated through UNKNOWN calibration, not silently assigned a ground-truth value.

## Catastrophic collapse

Frozen Candidate-v7 collapse definition is retained. A run catastrophically collapses if any of the following occurs:

- maximum predicted action share > `0.80`; or
- at least two required actions have zero recall; or
- invalid action count > `0`.

Required actions are the Protocol-v2 action set represented in that realization.

## Retry policy

Technical retry is allowed only for process crash, hardware interruption, corrupted output or deterministic serialization/runtime failure, only if no labels/ground truth were exposed to the candidate and only with the identical seed, dataset, candidate and configuration. Low score, family failure, forbidden ACT or collapse are never retryable scientific reasons.

## Integrity invalidation

The experiment becomes `V7R REQUALIFICATION INVALID — NO_ARCHITECTURE_CONCLUSION` if any material condition occurs, including candidate hash/config mutation, preregistration mutation, protected/legacy data contamination, label leakage to the runner, seed mutation, scorer access before prediction freeze, incomplete preregistered run count, selective rerun, threshold change, invalid scoring, manifest mismatch, or unauthorized tuning.

INVALID is not architecture failure and does not justify Candidate-v8.

## Terminal decision

Exactly one terminal state is permitted:

1. `V7R REQUALIFICATION PASS — FRESH_CONFIRMATORY_AUTHORIZED`
2. `V7R REQUALIFICATION FAIL — CANDIDATE_V7_QUALIFICATION_LINEAGE_TERMINATED`
3. `V7R REQUALIFICATION INVALID — NO_ARCHITECTURE_CONCLUSION`

A valid performance/safety failure is FAIL. An integrity/evaluation failure is INVALID. Gate G and Fresh Confirmatory are not executed in this mission.
