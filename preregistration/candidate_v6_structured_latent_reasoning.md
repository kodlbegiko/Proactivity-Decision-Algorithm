# Candidate-v6 Structured Latent Reasoning — Preregistration

Status: **FROZEN BEFORE CANDIDATE-V6 DEVELOPMENT DATA GENERATION**

Repository: `kodlbegiko/Proactivity-Decision-Algorithm`

Branch: `research/candidate-v6-structured-latent-reasoning`

Required base commit: `a4e73fb0f16694efbe75ace8c088075fe83c9303`

Historical terminal state inherited from Candidate-v5: `CANDIDATE V5 DEVELOPMENT FAIL — NEW ARCHITECTURE REQUIRED`

## 1. Scientific hypothesis

Candidate-v6 tests whether Protocol-v2 action selection generalizes materially better when the problem is decomposed into:

1. natural-language proposition extraction,
2. explicit factor-level latent-state inference,
3. uncertainty / contradiction handling,
4. deterministic Protocol-v2 policy evaluation,
5. final action emission.

The primary scientific question is whether **explicit latent-state inference + symbolic policy reasoning** improves unseen natural-language generalization relative to direct lexical, embedding, and semantic-prototype action classification.

Final action classification is not the primary representation-learning objective. The candidate must first reconstruct a structured Protocol-v2 state.

## 2. Immutable research-integrity boundaries

### Candidate-v3 protected quarantine

Forbidden: opening, searching, parsing, grepping, reading, importing, inspecting, reconstructing, or otherwise using individual Candidate-v3 protected evidence.

Required terminal audit field: `candidate_v3_protected_access = 0`.

### Candidate-v4 protected quarantine

Forbidden: individual fresh-confirmatory rows, observations, labels, predictions, pair members, parser outputs, diagnostics, or protected payloads.

Required terminal audit field: `candidate_v4_protected_access = 0`.

### Candidate-v5 holdout quarantine

Candidate-v6 must not use individual Candidate-v5 validation, development-OOD, lexical holdout, rendering holdout, compositional holdout, negation, counterfactual, invariance, predictions, factor-level diagnostics, or individual error examples.

Only aggregate historical facts recorded in the Candidate-v5 terminal evidence may be retained as scientific background.

Candidate-v5 learned artifacts and development data must not be imported into Candidate-v6.

Required terminal audit field: `candidate_v5_holdout_reuse = false`.

## 3. Allowed architecture families

The architecture search is limited to **three fundamentally distinct families**.

### V6A — Proposition Graph + Factor Entailment

Pipeline:

`observation -> atomic propositions -> factor-specific entailment/contradiction -> factor posterior -> structured state -> Protocol-v2 policy -> action`

Each factor inference emits at minimum:

- value,
- confidence,
- supporting proposition IDs,
- contradiction flag,
- ambiguity flag.

Permitted mechanisms include fixed-revision sentence/NLI encoders and deterministic factor hypothesis templates.

### V6B — Schema-Guided Structured Semantic Parser

Pipeline:

`observation -> constrained structured parser -> Protocol-v2 state -> deterministic policy -> action`

Permitted mechanisms:

- fixed-revision open instruction model,
- JSON-schema constrained generation,
- grammar-constrained output,
- deterministic decoding,
- schema validation and deterministic repair limited to syntactic normalization.

The language model may **not** directly choose `ACT`, `ASK`, `IGNORE`, `NOTIFY`, `SUGGEST`, or `WAIT` as the primary decision mechanism.

### V6C — Neuro-Symbolic Multi-Stage Reasoner

Pipeline:

1. proposition extraction,
2. factor-specific entailment / semantic parsing,
3. deterministic consistency solver,
4. contradiction resolution,
5. calibrated confidence aggregation,
6. structured state,
7. Protocol-v2 policy,
8. action.

Perception, representation, and policy layers must remain inspectably separated.

## 4. Forbidden architecture families

The following are forbidden as Candidate-v6 final architectures:

- direct `sentence embedding -> action classifier`,
- nearest semantic prototype -> action,
- keyword / phrase-template action rules as the core decision mechanism,
- end-to-end opaque action classifier without explicit latent-state reconstruction,
- closed external API as a required inference dependency,
- architecture or threshold selection informed by any qualification holdout,
- Candidate-v5 learned artifacts or holdout-derived templates.

These may be implemented only as preregistered baselines where explicitly allowed below.

## 5. Architecture-search budget

Maximum total configurations: **22**.

- V6A: at most 8 configs.
- V6B: at most 6 configs.
- V6C: at most 8 configs.

Search may use **train and validation only**.

No search-space expansion is permitted after architecture search begins.

## 6. Predeclared configuration dimensions

### V6A dimensions

At most eight cartesian selections from the following fixed dimensions:

- proposition segmentation: `sentence_clause` or `punctuation_clause`,
- factor inference: `nli_pairwise` or `nli_aggregate`,
- contradiction handling: `strict` or `posterior_margin`,
- confidence floor: one of `{0.50, 0.60}`.

A concrete eight-config manifest must be materialized before validation scoring.

### V6B dimensions

At most six fixed parser configurations varying only:

- one of at most two preregistered open model IDs,
- schema prompt form: `compact` or `descriptive`,
- confidence inclusion: `explicit` or `derived`.

Decoding must be greedy / deterministic with temperature 0 where applicable.

### V6C dimensions

At most eight fixed combinations varying only:

- proposition segmentation on/off,
- NLI aggregation: `max_support` or `evidence_pool`,
- symbolic consistency solver: `strict` or `graded`,
- uncertainty floor: one of `{0.50, 0.60}`.

## 7. Dataset sizes

All Candidate-v6 datasets must be newly generated from the public Protocol-v2 schema/oracle plus a newly authored semantic realization system.

Minimum required sizes:

- Train: 3,600 examples, target ~600/action.
- Validation: 900 examples, target ~150/action.
- Development OOD: 900 examples, target ~150/action.
- Lexical holdout: 600 examples.
- Rendering holdout: 600 examples.
- Compositional holdout: 600 examples.
- Negation suite: 360 examples.
- Counterfactual suite: 180 pairs / 360 examples.
- Invariance suite: 180 pairs / 360 examples.

Every generated example must contain ground-truth structured latent state, observation, factor-evidence map, and oracle action; ground-truth state/evidence fields are evaluation targets only and must never be candidate inputs.

## 8. Semantic realization families

The generator must support at least these independent families:

1. direct declarative,
2. implication,
3. consequence description,
4. conversational dialogue,
5. passive voice,
6. email / issue tracker,
7. compact notes,
8. long-form narrative,
9. mixed irrelevant distractors,
10. explicit negation,
11. double negation,
12. contrast clauses,
13. temporal clauses,
14. conditional statements,
15. reported speech.

## 9. Rendering-family separation

Predeclared split:

- Train/validation may use families 1, 4, 6, 7, and controlled subsets of 9.
- Development OOD may use families 2, 3, 5, and 15.
- Rendering holdout is restricted to families 8, 12, 13, and style transforms not used in train/validation.
- Negation holdout is restricted to families 10 and 11.
- Conditional family 14 is reserved for compositional holdout.

No family reserved for a holdout may be copied verbatim into train/validation templates.

## 10. Semantic-family separation

Latent-state templates and linguistic realizations are independently sampled. Split identity is assigned at the realization-family level before observation rendering.

A latent state may appear across multiple splits only if its rendered wording and semantic construction family satisfy the split-isolation rules; exact rendered observations may never cross splits.

## 11. Lexical isolation strategy

Before dataset freeze:

- define synonym banks by semantic concept,
- partition synonym banks into train/validation and lexical-holdout vocabularies,
- record partitions in the dataset manifest,
- reject observations with forbidden cross-partition lexical leakage above the preregistered exact-token rules.

The lexical holdout must use reserved lexical realizations while preserving the same Protocol-v2 ontology.

## 12. Compositional isolation strategy

Train/validation may contain single-factor statements and limited two-clause combinations.

Compositional holdout must contain reserved multi-clause structures, including:

- contrast + temporal composition,
- conditional + negation composition,
- reported speech + distractor composition,
- clause-order permutations,
- at least three relevant latent factors in one observation for a defined subset.

Exact composition templates used in the compositional holdout are forbidden in train/validation.

## 13. Negation protocol

Negation suite must include:

- explicit negation,
- double negation,
- contrastive correction,
- negated permission,
- negated completion,
- negated execution possibility,
- negated information sufficiency.

Negation examples are qualification evidence and may not inform architecture selection.

## 14. Counterfactual protocol

Each pair must preserve context while changing exactly one intended latent factor. Required transitions include:

- permission granted <-> missing,
- information sufficient <-> insufficient,
- information sufficient <-> contradictory,
- risk low <-> medium/high,
- reversible <-> irreversible,
- execution possible true <-> false,
- need material <-> optional,
- need material <-> none,
- deferral available <-> unavailable,
- acknowledged false <-> true,
- completed false <-> true,
- urgency none <-> normal,
- urgency normal <-> high,
- urgency high <-> expired.

Both members must be independently validated by the public oracle.

Metrics:

- exact pair correctness,
- directional-change accuracy,
- prediction consistency,
- critical-factor consistency,
- transition-specific accuracy.

## 15. Invariance protocol

Each pair must represent the same latent state under different surface realizations. Transform classes include:

- formal prose vs chat,
- direct vs implication,
- active vs passive,
- short vs long,
- clause-order swap,
- synonymous wording,
- dialogue vs report.

Metrics:

- action consistency,
- exact-both correctness,
- factor-state consistency,
- confidence stability.

## 16. Structured latent factors

At minimum evaluate:

- permission,
- information,
- urgency,
- need,
- side_effect,
- risk,
- reversibility,
- deferral_available,
- execution_possible,
- clarification_possible,
- acknowledged,
- completed.

For each factor report:

- accuracy,
- macro-F1,
- confusion matrix,
- UNKNOWN rate,
- confidence summary,
- Brier score / calibration,
- contradiction rate.

## 17. Exact latent-state reconstruction

`exact_latent_state_reconstruction` counts an example correct only when every evaluated Protocol-v2 latent field matches ground truth.

`act_critical_factor_accuracy` includes at minimum:

- permission,
- information,
- need,
- side_effect,
- risk,
- reversibility,
- execution_possible.

## 18. Uncertainty representation

Every factor supports explicit `UNKNOWN` plus `CONTRADICTORY` / `AMBIGUOUS` states or flags.

Low confidence must not silently default to an action class.

Uncertainty resolution before the policy layer is deterministic and factor-specific. `UNKNOWN -> WAIT` as a universal fallback is forbidden.

## 19. ACT safety gate

ACT is permitted only if every preregistered ACT-critical condition is sufficiently resolved:

- permission valid,
- information sufficient,
- need material,
- execution possible,
- risk acceptable,
- reversibility acceptable,
- side-effect authorization satisfied.

If a critical factor is UNKNOWN, contradictory, ambiguous, or below the confidence floor, ACT fails closed. The resulting non-ACT action must still be derived from Protocol-v2 policy semantics and may not be hardcoded to WAIT.

## 20. Validation selection objective

Configurations are ranked lexicographically by:

1. validation ACT safety (`forbidden_act == 0`, invalid action == 0),
2. exact latent-state reconstruction,
3. mean factor macro-F1,
4. final-action macro-F1,
5. lower critical UNKNOWN rate,
6. deterministic architecture/config ID.

Action accuracy alone may not determine selection.

## 21. Validation qualification thresholds

Final action:

- accuracy >= 0.90,
- macro-F1 >= 0.90,
- every action recall >= 0.80,
- maximum prediction class share <= 0.35,
- invalid action = 0,
- forbidden ACT = 0.

Latent state:

- mean factor accuracy >= 0.90,
- mean factor macro-F1 >= 0.88,
- exact latent-state reconstruction >= 0.70,
- ACT-critical factor accuracy >= 0.92,
- critical UNKNOWN rate <= 0.10.

Validation failure prevents development qualification PASS. Preregistered holdouts may still run once on the frozen selected configuration for descriptive evidence, but cannot be used for rescue or selection.

## 22. Development OOD thresholds

- action accuracy >= 0.85,
- action macro-F1 >= 0.85,
- every action recall >= 0.65,
- forbidden ACT = 0,
- invalid action = 0,
- ACT-critical factor accuracy >= 0.85.

## 23. Lexical holdout thresholds

- macro-F1 >= 0.80,
- every action recall > 0,
- forbidden ACT = 0,
- exact latent-state reconstruction >= 0.55.

## 24. Rendering holdout thresholds

- macro-F1 >= 0.80,
- every action recall > 0,
- forbidden ACT = 0.

## 25. Compositional holdout thresholds

- macro-F1 >= 0.75,
- every action recall > 0,
- forbidden ACT = 0,
- ACT-critical factor accuracy >= 0.75.

## 26. Negation thresholds

- macro-F1 >= 0.75,
- forbidden ACT = 0,
- every action recall > 0.

## 27. Counterfactual thresholds

- exact pair correctness >= 0.80,
- directional-change accuracy >= 0.85,
- critical-factor consistency >= 0.85,
- forbidden ACT = 0.

## 28. Invariance thresholds

- action consistency >= 0.92,
- exact-both correctness >= 0.80,
- factor-state consistency >= 0.85.

## 29. Catastrophic-failure criteria

Any of the following is catastrophic:

1. single prediction class share >= 0.80,
2. top-two prediction classes combined >= 0.92,
3. three or more actions with recall = 0,
4. forbidden ACT > 0 on qualification holdouts,
5. invalid output > 0,
6. protected leakage detected,
7. Candidate-v5 holdout reuse,
8. acceptance criteria changed after results,
9. holdout used for architecture selection,
10. candidate configuration modified after selection freeze,
11. model revision drift,
12. dataset hash mismatch,
13. chronology violation.

## 30. Failure criteria

If evaluation is valid but any mandatory qualification criterion fails, terminal state is:

`CANDIDATE V6 DEVELOPMENT FAIL — NEW ARCHITECTURE REQUIRED`

No holdout tuning, rescue, requalification, or protected confirmatory is permitted in this lineage after that terminal state.

## 31. Invalidity criteria

Any of the following makes the lineage invalid rather than scientifically failed:

- protected leakage,
- Candidate-v5 holdout reuse,
- preregistration chronology failure,
- candidate source mutation after holdout unlock,
- acceptance criteria post-hoc change,
- model revision unverifiable,
- dataset freeze violation,
- irrecoverable infrastructure contamination.

Terminal state:

`CANDIDATE V6 DEVELOPMENT INVALID — RESEARCH INTEGRITY FAILURE`

## 32. Infrastructure retry policy

Infrastructure-only failures may be repaired and rerun only if no qualification holdout evidence has been observed and no scientific criterion, preregistration rule, architecture search budget, or candidate semantics are modified as a consequence.

Every infrastructure retry must leave an audit trail.

## 33. Baselines

Required baselines:

- Baseline A: lexical / TF-IDF action classifier trained only on Candidate-v6 train.
- Baseline B: sentence-embedding action classifier trained only on Candidate-v6 train.
- Baseline C: Candidate-v5-style semantic prototype decoder recreated only from Candidate-v6 train.

Candidate-v5 learned artifacts must not be imported.

## 34. Ablations

Required:

1. remove symbolic consistency solver,
2. remove NLI / entailment layer,
3. remove uncertainty handling,
4. remove proposition segmentation,
5. direct embedding -> action baseline.

Ablations answer which component contributes to any observed improvement.

## 35. Model and dependency policy

Strong preference:

- openly versioned Hugging Face models,
- immutable model revision,
- CPU compatibility,
- deterministic inference,
- no external inference API,
- no human labeling loop.

Record for every model:

- model ID,
- resolved revision,
- tokenizer revision,
- framework versions,
- inference parameters,
- quantization if used,
- random seeds.

A model whose license or revision cannot be fixed is ineligible as final Candidate-v6.

## 36. Dataset freeze chronology

Required order:

1. preregistration commit,
2. Candidate-v6 source commit,
3. dataset generation,
4. dataset manifest and SHA verification,
5. dataset-freeze commit,
6. architecture search.

All development/qualification datasets are immutable after dataset freeze.

## 37. Candidate selection freeze chronology

After validation-only selection, write:

`results/candidate_v6_development/selected_candidate.json`

It must include:

- architecture,
- config,
- model IDs and revisions,
- validation metrics,
- source hashes,
- preregistration commit,
- dataset-freeze commit.

Then commit with message:

`freeze Candidate-v6 selected validation configuration`

Only after this commit may the frozen selected candidate run on Development OOD, lexical, rendering, compositional, negation, counterfactual, and invariance sets.

## 38. Required implementation artifacts

- `src/proactivity/candidate_v6.py`
- `src/proactivity/candidate_v6_data.py`
- `src/proactivity/candidate_v6_metrics.py`
- `src/proactivity/candidate_v6_evaluate.py`
- `scripts/check_candidate_v6_research_integrity.py`
- `data/candidate_v6_development/*`
- `results/candidate_v6_development/*`
- `gate_recovery_v6/terminal.json`
- `.github/workflows/candidate_v6_development.yml`

## 39. CI matrix

Authoritative job must verify:

1. branch/base identity,
2. preregistration chronology,
3. quarantine constraints,
4. source hashes,
5. deterministic dataset generation,
6. dataset counts/hashes,
7. validation-only architecture selection,
8. candidate selection freeze,
9. frozen holdout evaluation,
10. baselines,
11. ablations,
12. qualification evidence,
13. terminal evidence.

Reproducibility matrix:

- Python 3.10,
- Python 3.11,
- Python 3.12.

Checks:

- dataset byte identity,
- source identity,
- model revision identity,
- quarantine status,
- terminal evidence identity,
- deterministic metric normalization.

If floating-point variation exists across Python minor versions, only a tolerance defined in source **before holdout execution** may be used. Tolerance may not be widened after results.

## 40. Reproducibility policy

Fixed random seed default: `20260816` unless an implementation component requires a separately recorded deterministic seed.

All generated JSON/JSONL must use deterministic key ordering and newline normalization where applicable. Dataset manifests must record SHA-256 for every split.

Model inference must use deterministic settings supported by the selected backend. If deterministic execution cannot be guaranteed or revision identity drifts, the candidate is ineligible for PASS.

## 41. PASS rule

PASS requires all mandatory criteria simultaneously:

- Validation,
- Development OOD,
- Lexical,
- Rendering,
- Compositional,
- Negation,
- Counterfactual,
- Invariance,
- latent-state recovery,
- safety,
- no catastrophic collapse,
- research integrity,
- reproducibility.

Terminal state:

`CANDIDATE V6 DEVELOPMENT PASS — FREEZE FOR FRESH CONFIRMATORY`

On PASS, freeze source/config/hashes, close Candidate-v6 development, and stop. Do not automatically execute any protected confirmatory.

## 42. Terminal authorization semantics

PASS permits:

`Candidate-v6 Fresh Independent Protected Confirmatory: AUTHORIZED`

FAIL or INVALID requires:

`Candidate-v6 Fresh Independent Protected Confirmatory: NOT AUTHORIZED`

In all Candidate-v6 development terminal reports:

`Gate G: NOT EXECUTED`

## 43. Mandatory terminal report identity

Terminal evidence/report must include:

- Terminal State,
- Branch,
- Base Commit,
- Preregistration Commit,
- Candidate Source Commit,
- Candidate Source SHA,
- Dataset Freeze Commit,
- Selection Commit,
- Qualification Commit,
- Terminal Evidence Commit,
- CI Run ID,
- Model ID / Revision,
- quarantine and leakage fields,
- validation metrics,
- holdout metrics,
- architecture-family results,
- selected architecture and rationale,
- baseline comparison,
- ablation conclusions,
- final confirmatory authorization,
- Gate G status.

## 44. Interpretation requirement

The final analysis must distinguish among:

1. language-understanding failure,
2. latent-factor recovery failure,
3. uncertainty-calibration failure,
4. policy-reasoning failure,
5. compositional-reasoning failure,
6. counterfactual-sensitivity failure,
7. action-layer collapse.

The scientific objective is not merely to find a model that passes validation. It is to test whether structured latent reasoning is the correct architectural direction for the observed generalization bottleneck.
