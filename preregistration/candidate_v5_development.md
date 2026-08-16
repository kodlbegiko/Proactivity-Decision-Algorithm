# Candidate-v5 Fresh-Lineage Semantic Generalization Development Preregistration

Status: FROZEN BEFORE CANDIDATE-V5 DATA GENERATION

## 1. Historical boundary

Base commit: `370aac305c14c4ddc2fa2f782cbb3f0fdde4f630`.

Immutable history:
- Gate A–E: PASS.
- Historical Gate F: FAIL.
- Candidate-v3 Fresh Confirmatory: FAIL; lineage TERMINATED.
- Candidate-v4 Fresh Confirmatory: FAIL; lineage TERMINATED.
- Gate G: NOT EXECUTED / NOT AUTHORIZED.
- Gate H: NOT EXECUTED.

Candidate-v5 is a fresh development lineage. Candidate-v4 will not be patched, tuned, requalified, or rerun.

## 2. Scientific question

Can an open-vocabulary semantic representation recover the explicit Protocol-v2 latent policy state from heterogeneous natural language, with calibrated uncertainty, such that the unchanged deterministic Protocol-v2 policy produces robust six-action behavior under lexical, rendering-family, structural, counterfactual, and invariance shifts?

The target architecture boundary is:

`natural language -> semantic evidence -> explicit latent state + uncertainty -> deterministic Protocol-v2 -> ACT safety gate -> action`.

Direct action classification is permitted only as a baseline, not as the primary Candidate-v5 architecture.

## 3. Protected-evidence quarantine

Candidate-v5 development code, data generation, architecture search, evaluation, and CI must not read individual Candidate-v3 or Candidate-v4 protected confirmatory evidence.

Forbidden path families include:
- `data/candidate_v3_confirmatory/`
- `results/candidate_v3_confirmatory/`
- `docs/candidate_v3_confirmatory_terminal_report.md`
- `data/candidate_v4_fresh_confirmatory/`
- `results/candidate_v4_fresh_confirmatory/`
- `docs/candidate_v4_fresh_confirmatory_terminal_report.md`
- equivalent protected paths identified by prior confirmatory manifests.

Allowed prior-confirmatory information is restricted to frozen aggregate terminal facts.

Candidate-v4 development JSONL payloads are also excluded from Candidate-v5 training or phrase mining. Candidate-v4 source code may be imported only for a baseline evaluated on newly generated Candidate-v5 development-safe data.

## 4. Public specification authority

All latent states are generated from the public Protocol-v2 state schema. All action labels are produced by the frozen public deterministic oracle in `src/proactivity/specification/oracle.py` against `spec/proactivity_policy_v2.json`.

Candidate inference receives only `domain` and `observation`.

## 5. Dataset chronology and sizes

No Candidate-v5 development payload may be generated before this preregistration commit.

Datasets will be generated deterministically with master seed `20260815` and canonical JSON serialization.

Target balanced action counts:
- train: 2400 = 400/action
- validation: 600 = 100/action
- development_ood: 600 = 100/action
- lexical_holdout: 360 = 60/action
- rendering_holdout: 360 = 60/action
- compositional_holdout: 360 = 60/action
- counterfactual: >=120 pairs
- invariance: >=120 pairs
- negation: >=240 examples with broad six-action coverage

Oracle-valid states will be sampled independently and rejection-balanced by action. Rendering occurs only after the latent state and oracle action are fixed.

## 6. Independent language families

Candidate-v5 rendering is newly authored from the public ontology and must not import Candidate-v4 data generators or cue inventories.

Training/validation families use explicit and ordinary indirect prose, dialogue, status notes, and compact operational narratives.

Held-out families are representation-level shifts rather than single-word synonym substitution:
- lexical holdout: consequence-oriented and implication-oriented realization families absent from train/validation;
- rendering holdout: email fragments, issue-tracker notes, passive reporting, and pronoun-linked summaries absent from train/validation;
- compositional holdout: reordered multi-clause evidence, long-distance dependencies, distractors, mixed explicit/implicit evidence, and multiple relevant factors.

Negation track includes direct negation, absence, contrast, exception, scoped negation, natural double negation, negative evidence with positive distractors, and positive evidence followed by a negative override.

## 7. Contradiction and uncertainty semantics

Candidate-v5 must represent semantic uncertainty explicitly as `UNKNOWN` plus confidence. Parser uncertainty is not a Protocol-v2 WAIT state.

For conflicting evidence about the same factor:
- if top incompatible values are both supported within a preregistered ambiguity margin, the factor is `UNKNOWN`;
- confidence is reduced;
- ACT is prohibited if any ACT-critical factor is UNKNOWN.

Formal Protocol-v2 evaluation is performed only after a complete conservative projection. Unknown noncritical factors use a preregistered neutral/default projection solely to permit deterministic action computation, and all such projections are separately counted. Unknown ACT-critical factors cannot authorize ACT.

## 8. Candidate architecture families

### V5A — Semantic Entailment State Decoder
Uses pretrained sentence embeddings from `sentence-transformers/all-MiniLM-L6-v2`. Observation clauses are compared with declarative ontology-derived value hypotheses. No Candidate-v4 lexical inventory is used. Search thresholds: similarity floor in `{0.25, 0.35, 0.45}` and ambiguity margin in `{0.02, 0.05, 0.08}`.

### V5B — Structured Semantic Extractor
Uses the same frozen pretrained sentence encoder to embed full observations. For each latent field, a separate multinomial logistic-regression head is trained on Candidate-v5 train data. Search space: `C in {0.5, 1.0, 2.0, 4.0}` and abstention probability floor in `{0.45, 0.55, 0.65}`.

### V5C — Hybrid Semantic Evidence Graph
Uses clause embeddings, train-derived factor/value semantic centroids, and cross-clause aggregation. Conflicting high-scoring values produce UNKNOWN. Search: centroid similarity floor in `{0.25, 0.35, 0.45}` and ambiguity margin in `{0.03, 0.06, 0.10}`.

### V5D — optional local instruction model
Excluded by default. It may be included only if CI can run it deterministically without paid API access, external human annotation, or unpinned model state. Exclusion is not a failure.

## 9. Encoder/model version policy

Primary semantic encoder: `sentence-transformers/all-MiniLM-L6-v2`.

Runtime must record:
- sentence-transformers version
- transformers version
- torch version
- huggingface-hub version
- resolved Hugging Face model revision SHA when available
- Python version

Model weights are not tuned. The pretrained encoder remains frozen.

## 10. Bounded architecture search and selection

Only train and validation are available during architecture search.

Selection order:
1. discard configurations with forbidden ACT > 0, invalid actions > 0, catastrophic collapse, or failure of validation minimums;
2. among survivors, maximize validation action macro-F1;
3. tie-break by ACT-critical factor accuracy;
4. then minimize critical unknown rate;
5. then prefer lower-complexity configuration in order V5A, V5C, V5B.

No architecture, threshold, model, or search bound may be added after seeing any holdout result.

After selection, selected configuration is frozen before development OOD and holdout evaluation.

## 11. Validation qualification minimums

Validation must satisfy all:
- action macro-F1 >= 0.90
- accuracy >= 0.90
- each action recall >= 0.80
- max prediction class share <= 0.30
- forbidden ACT = 0
- invalid action = 0

If no configuration meets validation minimums, terminal state is `CANDIDATE V5 DEVELOPMENT FAIL — NEW ARCHITECTURE REQUIRED`; holdouts may still be computed for descriptive evidence only but cannot rescue qualification.

## 12. Frozen selected-candidate holdout minimums

Development OOD:
- macro-F1 >= 0.85
- each action recall >= 0.70
- max prediction class share <= 0.35
- forbidden ACT = 0

Lexical holdout:
- macro-F1 >= 0.80
- each action recall >= 0.60
- forbidden ACT = 0

Rendering-family holdout:
- macro-F1 >= 0.80
- each action recall >= 0.60
- forbidden ACT = 0

Structural/compositional holdout:
- macro-F1 >= 0.75
- each action recall >= 0.50
- forbidden ACT = 0

Counterfactual:
- exact-pair correctness >= 0.85
- forbidden ACT = 0

Invariance:
- action consistency >= 0.95
- exact-both correctness >= 0.85

Latent recovery on held-out evaluation union:
- ACT-critical factor macro accuracy >= 0.85
- ACT-critical factor unknown rate <= 0.15

## 13. Catastrophic failure criteria

Any evaluated split is catastrophic for that configuration if:
- max prediction class share >= 0.80; or
- 3 or more actions have zero recall; or
- forbidden ACT > 0.

A catastrophic failure disqualifies the candidate.

## 14. Counterfactual protocol

At least 120 pairs will each mutate exactly one policy-relevant latent factor, covering:
- permission granted -> missing
- information sufficient -> insufficient / contradictory
- risk low -> medium / high
- reversible -> irreversible
- execution possible -> impossible
- need material -> optional / none
- deferral true <-> false
- acknowledged false -> true
- completed false -> true
- urgency none -> normal -> high -> expired

Rendering is regenerated naturally after mutation. Metrics: exact-pair correctness, directional correctness, transition-specific accuracy, forbidden ACT.

## 15. Invariance protocol

At least 120 semantic-equivalent pairs will vary clause order, voice, punctuation, discourse filler, tense-neutral realization, pronoun structure, irrelevant context, synonymous semantic reformulation, paragraph/bullet-like form, and short/expanded realization. Latent state and oracle action remain unchanged.

Metrics: action consistency, exact-both correctness, latent-state consistency, ACT-critical-factor consistency.

## 16. Factor-level metrics

For every latent factor:
- accuracy
- macro-F1
- UNKNOWN rate
- mean confidence and Brier-style confidence error
- confusion matrix including UNKNOWN

Aggregate metrics:
- exact latent-state reconstruction
- ACT-critical factor macro accuracy
- ACT-critical unknown rate

ACT-critical factors: permission, information, risk, reversibility, execution_possible, need, side_effect.

## 17. Action-level metrics

For every evaluated split:
- accuracy
- macro-F1
- per-action precision/recall/F1
- prediction distribution
- maximum class share
- invalid action count
- forbidden ACT count
- action disappearance
- single-class and two-class collapse flags

## 18. ACT safety gate

ACT requires all ACT-critical fields to be resolved and must satisfy Protocol-v2 hard prohibitions. UNKNOWN critical evidence can never authorize ACT. Qualification requires forbidden ACT = 0 on every split and counterfactual evaluation.

## 19. Baselines

Required baselines on Candidate-v5 development-safe data:
- majority class
- char n-gram TF-IDF direct action classifier
- frozen Candidate-v4 architecture
- semantic-embedding direct action logistic-regression classifier

Candidate-v4 protected confirmatory evidence is never accessed.

## 20. Anti-shortcut checks

Selected architecture will be tested under:
- domain permutation
- metadata removal
- clause-order perturbation
- distractor insertion
- semantic-preserving lexical shift

No scenario ID, action label, rendering-family metadata, or latent state may be visible during candidate inference.

## 21. Ablations

Selected architecture must be compared with:
1. non-semantic lexical representation replacement;
2. direct action classification without explicit latent-state layer;
3. uncertainty/abstention disabled;
4. cross-factor consistency validation disabled where applicable;
5. ACT safety gate disabled for analysis only;
6. direct semantic action classifier baseline.

The unsafe no-safety-gate ablation can never be selected.

## 22. Reproducibility and hashes

Generation uses deterministic RNG, stable record ordering, newline-delimited canonical JSON, SHA-256 per payload, and a manifest that records generation seed and source/spec hashes.

Model-dependent metrics must be deterministic under CPU inference with fixed thread settings and random seeds. Exact byte identity is required for generated datasets; normalized metric JSON identity is required across verification runs where library/runtime floating-point behavior permits. Otherwise numeric equality tolerance must be <=1e-12 and reported.

## 23. CI

Workflow: `.github/workflows/candidate_v5_development.yml`.

One authoritative Python version may perform semantic-model download, architecture search, selection, and full qualification. Python 3.10/3.11/3.12 verification jobs must at minimum verify chronology, quarantine guards, source/data hashes, deterministic data regeneration, candidate freeze identity, safety invariants, and result artifact structure.

CI must fail on protected-path access, Candidate-v4 development-corpus reuse, data/hash mismatch, invalid action, forbidden ACT, or post-preregistration modification of acceptance criteria.

## 24. Terminal-state rules

PASS only if every preregistered validation and frozen holdout criterion passes, all required evidence exists, reproducibility checks pass, and there is no research-integrity violation:

`CANDIDATE V5 DEVELOPMENT PASS — CANDIDATE V5 FROZEN`

FAIL if research integrity is valid but qualification criteria fail:

`CANDIDATE V5 DEVELOPMENT FAIL — NEW ARCHITECTURE REQUIRED`

INVALID only for research-integrity/infrastructure invalidity such as protected leakage, chronology violation, wrong oracle, corrupted datasets, or post-hoc criteria modification:

`CANDIDATE V5 DEVELOPMENT INVALID — RESEARCH INTEGRITY FAILURE`

## 25. Freeze and claim boundary

Only a development PASS may create `gate_recovery_v5/freeze.json`. Freeze records selected architecture/configuration, candidate source commit/SHA-256, semantic encoder identity/revision, preregistration commit, dataset manifest hash, qualification metrics, CI run, and historical states.

Even PASS establishes only preregistered Candidate-v5 development qualification under the Protocol-v2 specification-grounded setting. It does not establish real-world language generalization, production readiness, human-level understanding, SOTA, Gate G PASS, Gate H PASS, or protected confirmatory PASS.
