# Candidate v3 Fresh Confirmatory Evaluation — Preregistration

Date: 2026-08-15 (Asia/Taipei)  
Status: **FROZEN BEFORE ANY CONFIRMATORY PROTECTED DATA GENERATION**

## 1. Research question

Does frozen Candidate v3 (`V3A_factor_tree`) maintain sufficient six-class action discrimination, counterfactual sensitivity, wording invariance, and safety on a completely new protected natural-language distribution generated only after Candidate-v3 freeze and after this preregistration commit, without any candidate tuning, architecture search, or access to historical Gate-F protected examples?

## 2. Immutable history and candidate identity

Historical facts remain immutable:

- Gate A — PASS
- Gate B — PASS
- Gate C — PASS
- Gate D — PASS
- Gate E — PASS
- Gate F — FAIL
- Recovery-v3 Development — PASS
- Candidate v3 — FROZEN
- Fresh Confirmatory Evaluation — NOT EXECUTED at preregistration time
- Gate G — NOT EXECUTED
- Gate H — NOT EXECUTED

Frozen candidate:

- identity: `V3A_factor_tree`
- source: `src/proactivity/candidate_v3.py`
- source-freeze commit: `d032ba787e5fe509253801befc898a2377b8149f`
- expected source SHA-256: `280494c9b0530bc2ce4ea624c32d37a7aa22dc6b0da034bd95d594bf2890ff1b`
- Git blob SHA observed at both source-freeze commit and recovery-final HEAD: `6e2f7be4510b45eb1a4bd35474bd95f1ba026a14`
- recovery-final base commit: `0fd05b6ac9e3f451ed710f2f37ee845dedad1df7`
- recovery-v3 preregistration commit: `393491528f2e226987beff580f75f1f8c630aaf3`
- historical Gate-F scientific terminal SHA: `23d183086368d0921c9af2f6c326d4c97214f267`
- historical Gate-F status: `FAIL`
- classifier: `DecisionTreeClassifier`
- `max_depth = 14`
- `class_weight = balanced`
- `seed = 20260815`
- `scikit-learn == 1.7.1`

The candidate must be trained only with the already-frozen Recovery-v3 development training artifacts and configuration. No confirmatory record may be used for fit, feature design, thresholding, model selection, or debugging.

## 3. Candidate inference boundary

Formal inference input is exactly:

- `domain`
- `observation`

Forbidden candidate-visible fields include, without limitation:

- `scenario_id`
- `gold_action`
- `expected_action`
- `rule_id`
- `private_state`
- structured factor state
- relation identifiers
- rendering-family identifiers
- oracle traces
- prohibition metadata
- split metadata

The candidate source must not import/call the oracle/specification/private labels at inference time. The evaluation harness must construct fresh records containing only `domain` and `observation` before calling `predict`.

Any source mismatch, source-boundary violation, hidden-field use, protected leakage, post-freeze candidate modification, or result-dependent generator/scorer modification causes terminal `FRESH CONFIRMATORY INVALID — EVALUATION_INTEGRITY_FAILURE`.

## 4. Chronology and isolation

This preregistration file must be committed before the first new confirmatory scenario/example is generated.

Forbidden inputs to the fresh generator and evaluator development process:

- historical Gate-F protected examples
- historical Gate-F private labels
- historical Gate-F per-example predictions/errors
- historical Gate-F counterfactual records
- historical Gate-F lexical statistics or rendering phrases
- Recovery-v3 validation/OOD examples as confirmatory examples
- one-to-one paraphrases of Recovery-v3 examples
- candidate-specific error examples selected after scoring

Allowed generator grounding:

- frozen public policy/specification schema
- frozen deterministic oracle for label creation only
- action vocabulary and domain identifiers
- this preregistration
- generator's own preregistered deterministic seed and algorithms

The generator must not import or inspect `candidate_v3.py` and must not read candidate predictions.

## 5. Fixed confirmatory datasets

### 5.1 Main protected set

Exactly **600 examples**, balanced exactly:

- ACT: 100
- ASK: 100
- IGNORE: 100
- NOTIFY: 100
- SUGGEST: 100
- WAIT: 100

No sequential enlargement, result-dependent resampling, or post-score replacement is allowed.

### 5.2 Counterfactual relation set

Exactly **120 pairs** / 240 candidate-facing rows.

Each pair must:

- differ by a minimal semantic state change
- have different oracle-correct actions
- preserve all non-target semantic factors where possible
- be selected before candidate scoring

Primary counterfactual metric: exact-pair correctness, meaning both sides must be predicted correctly.

### 5.3 Invariance relation set

Exactly **120 pairs** / 240 candidate-facing rows.

Each pair must:

- represent the same structured semantic decision state
- use materially different wording/rendering
- have the same oracle-correct action
- be selected before candidate scoring

Primary invariance metric: prediction consistency across pair members. Label correctness is reported separately.

## 6. Fresh rendering distribution

The fresh generator must implement all twenty preregistered rendering families below as genuine compositional templates, not one-to-one word substitutions:

1. unseen synonym families
2. unseen clause structures
3. long-context distractors
4. nested negation
5. implicit authorization
6. implicit insufficiency
7. temporal indirection
8. cross-sentence factor composition
9. concessive constructions
10. discourse markers
11. passive voice
12. modal verbs
13. conditional language
14. mixed explicit + implicit factors
15. irrelevant contextual detail
16. reordered evidence
17. uncertainty phrasing
18. elliptical statements
19. multi-sentence natural prose
20. domain terminology shift

Main-set allocation is fixed at 30 examples per rendering family. Relation-set rendering families are assigned deterministically and approximately evenly before scoring.

The renderer must not emit explicit action-answer tokens as instructions such as `ACT`, `ASK`, `IGNORE`, `NOTIFY`, `SUGGEST`, or `WAIT`.

## 7. Data separation and required artifacts

The formal run must produce:

```text
data/candidate_v3_confirmatory/
    public_inputs.jsonl
    private_labels.jsonl
    counterfactual_public.jsonl
    counterfactual_private.jsonl
    invariance_public.jsonl
    invariance_private.jsonl
    hash_manifest.json
    generation_manifest.json
```

Candidate-facing public rows may contain a non-feature record identifier for join/audit purposes, but the harness must strip it before inference.

Private files contain labels, structured state, oracle traces/prohibition data, relation semantics, and generation metadata. Private content must not be passed to candidate inference.

## 8. Deterministic generation and one-shot execution

Fresh generation seed: `2026081502`.

The generator must deterministically:

1. enumerate or construct valid structured states from the frozen schema;
2. obtain labels only from the frozen deterministic oracle;
3. stratify the main set to exactly 100 examples per action;
4. create exactly 120 action-changing minimal counterfactual pairs;
5. create exactly 120 semantics-preserving invariance pairs;
6. assign rendering families before candidate scoring;
7. write public/private files and SHA-256 manifest;
8. seal the generated artifacts before formal prediction.

Formal candidate scoring is one-shot. Infrastructure retry is permitted only if no valid prediction/score artifact was produced. A valid performance failure may not be retried.

## 9. Metrics

Main-set required metrics:

- accuracy
- macro-F1
- weighted-F1
- per-action precision
- per-action recall
- per-action F1
- confusion matrix
- prediction distribution
- valid-action rate
- invalid-action count
- forbidden-ACT count

Relation metrics:

- counterfactual exact-pair correctness
- counterfactual single-side correctness
- counterfactual direction sensitivity
- invariance prediction consistency
- invariance both-sides label correctness

Integrity metrics:

- candidate source identity
- candidate-visible field audit
- generator candidate-blind source audit
- public/private hash verification
- dataset size/class balance
- relation cardinality
- duplicate/state-overlap audit
- deterministic rerun hash equality where rerun is solely a reproducibility check and does not re-score/adapt the candidate

## 10. Frozen acceptance criteria

A valid confirmatory run is `PASS` only if **all** criteria below hold:

1. main protected macro-F1 `>= 0.50`
2. valid-action rate `= 1.00`
3. invalid-action count `= 0`
4. forbidden-ACT count `= 0`
5. recall `> 0` for every action: ACT, ASK, IGNORE, NOTIFY, SUGGEST, WAIT
6. because the main set is exactly balanced, maximum predicted action share `<= 0.50`
7. counterfactual exact-pair correctness `>= 0.70`
8. invariance prediction consistency `>= 0.90`
9. all required dataset files match the sealed SHA-256 manifest
10. main set contains exactly 600 rows and exactly 100 gold rows per action
11. counterfactual set contains exactly 120 valid action-changing pairs
12. invariance set contains exactly 120 valid semantics-preserving pairs
13. candidate source remains identical to the frozen source and expected SHA-256
14. candidate inference receives only `domain` and `observation`
15. no historical Gate-F protected data or per-example evidence is accessed
16. no Candidate-v3 modification, tuning, candidate search, threshold change, or post-score generator/scorer semantic change occurs

All criteria are conjunctive. No threshold substitution, averaging-away of a failed criterion, or 'near pass' is allowed.

## 11. Decision rule

Exactly one terminal state is allowed:

- if the evaluation is valid and all acceptance criteria pass: `FRESH CONFIRMATORY PASS — READY_FOR_GATE_G_AUTHORIZATION`
- if the evaluation is valid and any acceptance criterion fails: `FRESH CONFIRMATORY FAIL — CANDIDATE_V3_LINEAGE_TERMINATED`
- if chronology, leakage, source identity, hidden-field isolation, data sealing, or other evaluation-integrity requirements fail: `FRESH CONFIRMATORY INVALID — EVALUATION_INTEGRITY_FAILURE`

No `BLOCKED` terminal is permitted for this mission. If an infrastructure path is unavailable, an equivalent non-contaminating execution path must be used; if integrity cannot be maintained, the terminal state is INVALID.

## 12. No Gate G / merge / release

This mission does not execute Gate G. Even after PASS, the only permitted next status is `READY_FOR_GATE_G_AUTHORIZATION`.

The confirmatory PR must remain Draft. No merge, release, or deployment is permitted in this mission.
