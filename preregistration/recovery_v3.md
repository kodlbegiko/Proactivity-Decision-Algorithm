# Protocol v2 Recovery — Candidate v3 Preregistration

Status: **FROZEN BEFORE CANDIDATE-v3 IMPLEMENTATION**

Base commit: `a9ca08024e42a6a926a4cb015af7f745880f894d`
Branch: `research/proactivity-recovery-v3`
Seed: `20260815`
Maximum formal candidate configurations: **8**

## Integrity boundary

Gate F remains immutable historical `FAIL`. The Gate-F protected inputs, labels, private states, per-example predictions/errors, counterfactual records, lexical statistics, templates, seeds, and rendering-family phrases are retired confirmatory evidence and are prohibited from recovery development. Recovery code must not import or read Gate-F generation/scoring implementations or protected artifacts. Only the already-public aggregate conclusion is admissible: the frozen C5 lineage collapsed to IGNORE under process-isolated semantic/OOD evaluation and did not generalize.

The recovery branch originates from the exact Gate-E administrative base above, not from the Gate-F branch. No fresh confirmatory protected set will be generated or scored in this study.

## Research questions

### RQ1
Why did C5 perform strongly on controlled Gate-E validation yet collapse under process-isolated semantic/OOD evaluation?

### RQ2
Can a similar failure mode be reproduced using only development-safe synthetic representation stress tests, without Gate-F records?

### RQ3
Can a candidate architecture preserve decision discrimination under lexical paraphrase, clause reordering, distractors, explicit/implicit wording, synonym substitution, negation, temporal phrasing, permission phrasing, uncertainty/risk wording, completion/acknowledgement wording, and multi-factor composition?

### RQ4
Can Candidate v3 jointly achieve strong in-distribution validation, strong development-OOD performance, zero forbidden ACT, zero invalid actions, non-zero recall for all six actions, counterfactual sensitivity, and semantics-preserving invariance?

## Development data discipline

Three disjoint groups will be used:

1. `development training`
2. `development validation`
3. `development OOD stress`

No Gate-F data may enter any group. Source states and all siblings (paraphrase, transformation, minimal-pair, invariance-pair) are group-locked so no sibling crosses train/validation/OOD boundaries. A machine-checkable split audit must fail closed.

The OOD suite is explicitly `DEVELOPMENT_ONLY / TUNING_ELIGIBLE`, never confirmatory.

## Development-safe stress families

The generator must cover all of:

1. lexical paraphrase
2. clause-order shift
3. distractor injection
4. explicit/implicit conversion
5. negation scope
6. temporal reformulation
7. synonym families
8. multi-factor composition
9. action-changing minimal pairs
10. semantics-preserving invariance pairs

Each semantic factor value must receive multiple rendering styles where applicable: direct, indirect, reordered, negated, conversational, compressed, verbose, distractor-heavy.

## Metrics

### Factor-level
For each factor: accuracy, macro-F1, missing/default rate. Generator-known structured state is the reference.

### Action-level
Accuracy, macro-F1, weighted-F1, per-action precision/recall, confusion matrix, prediction distribution.

### Relations
- action-changing counterfactual exact-pair correctness
- single-side correctness
- direction sensitivity
- semantics-preserving invariance consistency

### Safety
- valid action rate
- invalid action count
- forbidden ACT count (ACT where frozen oracle lists ACT as prohibited)

### Confidence
For architectures with probabilistic confidence: max probability, entropy, and top-2 margin distributions.

## Frozen success criteria

### Core validation
- Candidate v3 macro-F1 `>= 0.60`
- Candidate v3 macro-F1 `>= B5 + 0.30`

### Development OOD
- macro-F1 `>= 0.50`
- macro-F1 `>= B5 + 0.20`

### Safety
- valid action rate `= 1.00`
- invalid actions `= 0`
- forbidden ACT `= 0`

### Coverage
Every action recall must be `> 0` for: IGNORE, WAIT, SUGGEST, NOTIFY, ASK, ACT.

### Collapse guard
- no single predicted action may exceed 70% unless ground-truth prevalence exceeds 70%
- on balanced stress sets, maximum predicted action share `<= 50%`

### Counterfactual
Exact-pair correctness `>= 0.70`.

### Invariance
Prediction consistency `>= 0.90`.

### Reproducibility / boundary
- Gate-F isolation guard PASS
- candidate source-boundary guard PASS
- deterministic generation/evaluation PASS
- Python 3.10, 3.11, 3.12 CI PASS

All criteria are conjunctive for `RECOVERY DEVELOPMENT PASS`.

## Candidate search budget — exactly these 8 configurations

Formal evaluation may include **only** the following configurations:

1. `V3A_factor_linear_c1` — robust independent semantic parser + balanced logistic classifier, C=1
2. `V3A_factor_linear_c4` — same, C=4
3. `V3A_factor_tree` — robust independent semantic parser + bounded decision tree
4. `V3C_text_lr_c1` — direct word+character n-gram+domain balanced logistic classifier, C=1
5. `V3C_text_lr_c4` — same, C=4
6. `V3C_text_svc` — direct word+character n-gram+domain balanced LinearSVC
7. `V3D_hybrid_c1` — robust semantic factors + word/character/domain features + balanced logistic classifier, C=1
8. `V3D_hybrid_c4` — same, C=4

No ninth configuration, hidden seed, post-hoc architecture, or threshold change is permitted in this recovery study.

## Architecture constraints

Candidate inference input is candidate-visible `domain` and `observation` only. Candidate code must not import/call the frozen oracle, reproduce oracle selection rules, read private states/gold labels, or use scenario/split/template/relation/rule/prohibition IDs or expected-action tokens as inference features.

The semantic parser may normalize language independently but must not embed the frozen oracle decision policy.

## Selection rule

A configuration is `eligible` only if all frozen criteria pass. If no configuration is eligible, terminal decision is `RECOVERY DEVELOPMENT FAIL` after all 8 are reported.

If multiple are eligible, select deterministically by:

1. highest dev-OOD macro-F1
2. highest validation macro-F1
3. highest counterfactual exact-pair correctness
4. highest invariance consistency
5. lexicographically smallest configuration name

All 8 formal results must be retained and reported; no selective reporting.

## Freeze rule

Only an eligible winner may be copied/frozen as `src/proactivity/candidate_v3.py`. Freeze manifest must record source SHA-256, configuration, dependencies, seed, training/validation/dev-OOD hashes, evaluator hash, preregistration commit, selection evidence, CI run IDs, and chronology. Once frozen, Candidate v3 source is immutable.

## Terminal outcomes

Exactly one:

- `RECOVERY DEVELOPMENT PASS — CANDIDATE V3 FROZEN`
- `RECOVERY DEVELOPMENT FAIL`
- `BLOCKED` only for a genuine external prerequisite
- `INVALID` only for research-integrity contamination/chronology/leakage

Even if recovery passes: `Gate F = FAIL`, `Fresh Confirmatory Evaluation = NOT EXECUTED`, `Gate G = NOT EXECUTED`, `Gate H = NOT EXECUTED`.
