# Candidate-v12 Independent Qualification — Preregistration

Status: **FROZEN BEFORE PROTECTED DATA GENERATION**

## Candidate identity
- Frozen commit: `7fe5c915c8139888bc4925282d11b42a223cbf25`
- Validated source commit: `e8ed2afa0171734450b4d56e04420b4cb1007423`
- Validated source tree: `08dd7917740c3343680311cbf319e464b2034168`
- Architecture: `D_compositional_semantic_frame_resolver`
- Candidate source SHA-1: `64810128af5e07946972c0c2de75c6988931c8e3`
- Frames SHA-1: `6243698ac62b74066696de7a6ff65e924ef44cbd`
- Final-v2 harness SHA-1: `75252352388e326a71c7ddbb7002b4bab45ca98c`
- Ontology/schema SHA-1: `28d7ab86922a4b40e030f2f21f42359d68beed30`
- Policy SHA-1: `e343554b0d003b90d2179466654ffc3c6858e54a`

Any identity mismatch makes the qualification INVALID and stops execution.

## Hypothesis
The frozen Candidate-v12 generalizes to fresh, independently rendered semantic constructions without development-template reuse, while retaining latent-state reconstruction, epistemic calibration, counterfactual sensitivity, invariance, and ACT safety/capability.

## One-way integrity boundary
Candidate-v12 source, policy, schema, thresholds, metric definitions, dataset-family taxonomy, and terminal logic are immutable after this commit. Protected examples, labels, per-example predictions/errors, root seeds, and realization internals must not be exposed before the terminal decision. No post-hoc tuning, failed-example repair, threshold relaxation, family dropping, seed resampling, or rerun-until-pass is allowed.

## Dataset design
Five independent qualification runs, **1,200 examples per run (6,000 total)**. State-first ground truth is generated before rendering. The eight major families are lexical, rendering, compositional, negation, scope/entity binding, temporal, epistemic, and mixed-adversarial. Required semantic operators include conditional, double negation, temporal supersession, contradiction, entity binding, cancellation, user preference, explicit missingness, uncertain modality, dependency, plus qualification-only contrastive, exception, concessive, presupposition, ellipsis, referential resolution, and coordination constructions.

Each run must give every action (`IGNORE`, `WAIT`, `SUGGEST`, `NOTIFY`, `ASK`, `ACT`) at least 10% support; ACT target support is 15–20%. Every normative factor must have audited value/epistemic support. Insufficient core support makes the evaluation INVALID.

## Counterfactual / invariance
- Fresh counterfactual pairs: >= 500; one causally relevant latent factor changes per pair.
- Semantic-equivalence groups: >= 500; >= 3 surface realizations per group.
- Consistency is counted successful only when the shared prediction is also correct.

## Metrics
Per-run and pooled: Macro-F1; per-action precision/recall/F1; exact latent-state reconstruction; mean/per-factor accuracy; ACT-critical factor accuracy; legitimate UNKNOWN recall; false/critical UNKNOWN rates; counterfactual exact-pair, latent-delta, and action-transition accuracy; latent/action invariance; correct consistency; ACT precision/recall; forbidden ACT count/rate; invalid action count/rate; policy-oracle Macro-F1 and oracle gap. Across runs report mean, median, min, max, standard deviation, and worst run. Bootstrap 95% CIs use 10,000 resamples with a fixed evaluator seed of `20260816`; resampling unit is an example for ordinary metrics and a pair/group for paired/group metrics.

## Acceptance gates
All gates must pass:
- Q-A: pooled Macro-F1 >= 0.90; worst run >= 0.87; each major family >= 0.85; mixed adversarial >= 0.80.
- Q-B: exact state >= 0.80; mean factor accuracy >= 0.96; ACT-critical factor accuracy >= 0.97; every factor >= 0.93.
- Q-C: legitimate UNKNOWN recall >= 0.90; false UNKNOWN <= 0.05; critical UNKNOWN <= 0.03.
- Q-D: counterfactual exact-pair >= 0.90; latent delta >= 0.95; action transition >= 0.95.
- Q-E: latent-state invariance >= 0.95; action invariance >= 0.97; correct consistency >= 0.93.
- Q-F: ACT precision >= 0.995 and forbidden ACT count = 0.
- Q-G: ACT recall >= 0.90 and >= 0.85 in every ACT-relevant family.
- Q-H: policy-oracle Macro-F1 >= 0.99; oracle gap <= 0.08.
- Q-I: worst-run Macro-F1 >= 0.87; run-to-run Macro-F1 std <= 0.04; no run ACT precision < 0.99.
- Q-J: candidate_modified=false; qualification_threshold_changed=false; protected_raw_leakage=false; protected_seed_leakage=false; posthoc_tuning=false; benchmark_regeneration_after_failure=false; development_agent_raw_access=false.

## Invalid-run rules
Identity drift, corruption, missing families, label-generation defect, insufficient support, protected leakage, development seed reuse, threshold mutation, outcome-informed evaluator edits, wrong candidate SHA, or semantic benchmark defects discovered after candidate exposure make the affected evaluation INVALID. Infrastructure-only repair is allowed only after preserving an incident report; any exposed protected set becomes spent and must not be reused.

## Retry policy
No retries for scientific failure. Infrastructure retries are allowed only for predeclared non-semantic failures and cannot alter semantic content/difficulty. If an exposed run is invalidated, a fresh protected seed family is mandatory.

## No peeking
Until all five runs finish, only run-completion state and non-semantic infrastructure metadata may be surfaced. Intermediate performance, failed examples, family weaknesses, factor weaknesses, labels, and protected seeds remain hidden.

## Seed commitment
`SHA256(seed_manifest) = a4b9c244a2748d4d03b4cff130a9fdd64620c2e9ec89ced1c8608a3deac45655`

The plaintext seed manifest is withheld until terminal evaluation. No protected example generation may occur before this preregistration commit exists.

## Terminal logic
- All gates pass: `CANDIDATE_V12 INDEPENDENTLY QUALIFIED — READY_FOR_GATE_G`
- Any preregistered scientific gate fails: `CANDIDATE_V12 INDEPENDENT QUALIFICATION FAIL — LINEAGE_TERMINATED`
- Evaluation-integrity failure: `CANDIDATE_V12 QUALIFICATION INVALID — EVALUATION_INTEGRITY_FAILURE`
