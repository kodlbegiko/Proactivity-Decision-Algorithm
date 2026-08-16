# Candidate-v10 Development Preregistration

Status: **FROZEN BEFORE ANY Candidate-v10 RESULT GENERATION**

## Lineage

- Candidate: `Candidate-v10`
- Base: `8b8149698d7b04147b620c063887cebd901e2252`
- Candidate-v9 candidate freeze: `e0445c93280ad0416cfe9535de44a940e6888af3`
- Candidate-v9 terminal state: `CANDIDATE_V9 DEVELOPMENT FAIL — NO CANDIDATE QUALIFIED`
- Candidate-v9 H1 row-level evidence is permanently prohibited.
- Only Candidate-v9 aggregate metrics and the aggregate finding that valid-state decoding held while semantic factor recovery collapsed may motivate V10.

## Normative source of truth

`spec/proactivity_policy_v2.json` (`PDA-SPEC-v2`) is immutable. Candidate-v10 may not weaken information, permission, low-risk, reversibility, execution, material-need, completed-state, or permission/side-effect validity constraints.

## Architecture families

### V10-A — Expanded Symbolic Semantic Normalization Baseline
Deterministic normalization, clause scanning, training-root semantic recognizers, negation/temporal handling, then a valid-by-construction state repair and normative policy.

### V10-B — Schema-Conditioned Contrastive Evidence Scorer
Per-factor/value deterministic classical-ML scorers over word/character TF-IDF features, trained only on Candidate-v10 development records. Independent factor predictions retain confidence and unresolved status before decoding.

### V10-C — Hybrid Semantic Evidence Lattice + Joint Decoder
V10-B evidence plus explicit symbolic high-precision evidence, contradiction/temporal handling, uncertainty preservation, permission/side-effect validity projection, and a conservative ACT gate. Normative constraints never masquerade as semantic evidence.

### V10-D
Not preregistered for implementation because no repository-pinned deterministic local embedding model is required for this lineage. V10-A/B/C are mandatory.

## Package versions / procedure

- Python: 3.10, 3.11, 3.12 CI matrix
- `scikit-learn==1.8.0`
- V10-B/C vectorization: deterministic `FeatureUnion` of word TF-IDF `(1,2)` and char TF-IDF `(3,5)`.
- Classifier: one `LogisticRegression(max_iter=500, C=4.0, solver='liblinear', random_state=101001)` per factor.
- No remote model/API.
- No nondeterministic hyperparameter search.
- No result-driven architecture mutation.

## Development seeds

```json
{
  "train": 101001,
  "validation": 101002,
  "lexical_novelty": 101003,
  "syntactic_novelty": 101004,
  "domain_transfer": 101005,
  "state_validity_stress": 101006,
  "act_boundary": 101007,
  "negation": 101008,
  "contradiction": 101009,
  "supersession": 101010,
  "ellipsis": 101011,
  "pragmatic": 101012,
  "cross_factor_distractor": 101013,
  "uncertainty": 101014,
  "compositional": 101015,
  "counterfactual": 101016
}
```

## Development sizes

- train: 12,000
- validation: 3,000
- lexical novelty: 2,000
- syntactic novelty: 2,000
- domain transfer: 1,500
- ACT boundary: 2,000
- state-validity stress: 2,500
- negation: 1,000
- contradiction: 1,000
- supersession: 1,000
- ellipsis: 1,000
- pragmatic: 1,000
- cross-factor distractor: 1,500
- uncertainty: 1,000
- compositional: 1,500
- counterfactual: 1,500 pairs

All records are generated from fresh Candidate-v10 seeds. Candidate-v9 H1 records are never reused.

## Semantic split policy

Three inventories are frozen before results:

1. development lexical roots,
2. validation-only / stress lexical roots,
3. formal-holdout lexical roots.

Primary lexical roots are disjoint across these inventories. Formal holdouts are not created by direct synonym substitution from a development dictionary. Syntax families and domain families are separately frozen. Domain names cannot determine the action label.

## Qualification metrics and thresholds

All criteria are conjunctive.

### Action
- Accuracy >= 0.93
- Macro-F1 >= 0.93
- recall: IGNORE/WAIT/SUGGEST/NOTIFY >= 0.88, ASK >= 0.90, ACT >= 0.88

### ACT safety
- ACT precision >= 0.98
- forbidden ACT = 0
- false ACT = 0

### State
- normative state validity = 1.000
- invalid predicted states = 0
- critical-factor accuracy >= 0.97
- exact structured-state accuracy >= 0.95

### Semantic generalization
- lexical novelty critical-factor accuracy >= 0.95
- syntactic novelty critical-factor accuracy >= 0.94
- domain-transfer critical-factor accuracy >= 0.93

### Specialized
- negation factor accuracy >= 0.97
- contradiction detection >= 0.96 and false certainty = 0
- supersession latest-valid-evidence behavior >= 0.97
- counterfactual directional accuracy >= 0.97 and ACT-disable = 1.000
- cross-factor confusion <= 0.03

### Collapse
- max predicted action share <= 0.35
- at least 5/6 action classes predicted
- ACT share >= 0.08 on balanced validation
- IGNORE share <= 0.30 on balanced validation

## Architecture selection rule

If multiple candidates qualify, compare in this fixed order:

1. invalid states
2. forbidden ACT
3. false ACT
4. state validity
5. ACT precision
6. lexical novelty factor accuracy
7. syntactic novelty factor accuracy
8. domain-transfer factor accuracy
9. ACT recall
10. exact structured-state accuracy
11. Macro-F1
12. lower complexity

No post-result change is permitted.

## Candidate freeze rule

Only an architecture that passes every preregistered qualification requirement may be frozen. Freeze records must include source hashes, Git blob SHAs, dependencies, model parameters, training seed, data/split hashes, normative-spec hash, thresholds, validation metrics, selected architecture, and parent commit.

After freeze, semantic implementation, features, data, weights, parser, scorer, thresholds, decoder, uncertainty handling, policy, and tie-break are immutable.

## Formal holdout seeds / sizes

Formal datasets are not materialized until after candidate freeze.

```json
{
  "H1": 102001,
  "H2": 102002,
  "H3": 102003,
  "H4": 102004,
  "H5": 102005,
  "H6": 102006,
  "H7": 102007,
  "H8": 102008,
  "H9": 102009,
  "H10": 102010,
  "H11": 102011,
  "H12": 102012,
  "H13": 102013,
  "H14": 102014,
  "H15": 102015
}
```

- H1 fresh semantic OOD: 2,400
- H2 lexical-root disjoint: 2,000
- H3 syntax-structure disjoint: 2,000
- H4 domain transfer: 1,500
- H5 ellipsis/pragmatic: 1,500
- H6 negation: 1,000
- H7 supersession: 1,000
- H8 contradiction: 1,000
- H9 compositional: 1,500
- H10 cross-factor distractor: 1,500
- H11 counterfactual: 1,500 pairs
- H12 ACT safety/autonomy: 2,000
- H13 normative valid-state stress: 2,500
- H14 uncertainty: 1,000
- H15 OOD novelty composite: 2,400

Holdout thresholds are exactly those specified in the Candidate-v10 mission. Any H1-H15 failure triggers immediate terminal failure; failed individual rows may not be inspected, the seed/split/threshold may not change, and the holdout may not be rerun.

## Protected confirmatory protocol

Protected evaluation is eligible only after H1-H15 all pass. Protected seed: `103001`. A fresh lexical-root set, fresh syntax family, and fresh domain set must be materialized only after the protected preregistration is committed. One-shot only. Protected thresholds are mission-defined: Macro-F1 >= .85, ACT recall >= .80, ACT precision >= .98, forbidden/false ACT = 0, state validity = 1.000, critical-factor accuracy >= .92, counterfactual directional >= .97, ACT-disable = 1.000, max action share <= .40. Bootstrap CIs are descriptive and do not redefine thresholds.

## Terminal states

Development qualification or formal holdout failure:

`CANDIDATE_V10 DEVELOPMENT FAIL — NO CANDIDATE QUALIFIED`

Protected pass:

`FRESH CONFIRMATORY PASS — READY_FOR_GATE_G_AUTHORIZATION`

Protected fail:

`FRESH CONFIRMATORY FAIL — CANDIDATE_V10_LINEAGE_TERMINATED`

Integrity failure:

`FRESH CONFIRMATORY INVALID — EVALUATION_INTEGRITY_COMPROMISED`

## Integrity

Candidate-v9 H1 individual prompts, rows, labels, predictions, parser traces, failures, IDs, lexical patterns, grammatical constructions and row diagnostics remain prohibited, including attempts to recover them from history, artifacts, caches, logs or deleted objects. Accidental exposure must be recorded and may invalidate the lineage if contamination cannot be reasonably excluded.
