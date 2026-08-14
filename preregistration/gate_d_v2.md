# Protocol v2 Gate D Preregistration — Baseline Integrity

Status: **FROZEN BEFORE FORMAL BASELINE EVALUATION**

Base commit: `b26aa39866e5cc7aa99ba97d71862f7550a447fe`  
Frozen upstream spec commit: `89e00052d68b2862269daf2adc8b31ebb1ae592c`  
Frozen benchmark: `benchmark_v2`, generator `2.0.1`, seed `20260814`, 168 scenarios.

## Scientific question

Does Protocol v2 have a deterministic, reproducible, leakage-controlled set of comparison baselines suitable for later candidate evaluation? Gate D assesses **baseline integrity**, not whether baseline performance is high.

## Candidate-visible fields and split use

Raw-context model inputs are limited to `domain` and/or `observation` as defined below. `scenario_id` may be used only as a join key and is removed before model fitting/prediction. Development split labels are the only labels permitted for fitting priors or learned baseline parameters. Validation labels are used only by the evaluator after predictions are produced. `protected_test` is not used for fitting, model selection, or Gate-D formal scoring.

Forbidden predictive inputs include private/oracle data, structured hidden state, matched rules, prohibition traces, template/split/family metadata, scenario identifiers, and direct gold-label lookup tables.

## Required baselines

- **B0 Majority Action**: choose the most frequent development action; deterministic lexical tie-break by action name if needed.
- **B1 Prior-Sampled Random**: sample actions according to development-label priors using NumPy-compatible deterministic PRNG seed `20260814`; validation row order is canonicalized before sampling.
- **B2 Domain-Only**: development majority action per domain, falling back to global development majority for unseen domains. Input: `domain` only.
- **B3 Simple Lexical**: word-unigram count features from `observation` with Multinomial Naive Bayes. Fixed `alpha=1.0`.
- **B4 Strong Classical Text**: fixed union of word TF-IDF `(1,2)` and character TF-IDF `(3,5)` from `observation`, plus one-hot `domain`; multinomial-capable logistic regression, fixed `C=1.0`, `max_iter=2000`, deterministic seed `20260814`. No external LLM/API.
- **B5 Transparent Heuristic**: fixed, hand-written, non-learning keyword rules over `domain + observation`, defined before formal scoring. It must not import oracle/spec implementation or read gold/private/structured files. The rule is intentionally simple and is not modified after seeing formal validation scores.

No PDA candidate tuning is allowed in Gate D.

## Dependency policy

Use Python standard library plus pinned `scikit-learn==1.8.0` for B3/B4 and metric recomputation. CI must exercise Python 3.10, 3.11, and 3.12. If this exact version is unavailable on a supported Python version, that is an infrastructure issue requiring an explicit amendment before formal evaluation; thresholds are not changed.

## Metrics

For every baseline on validation, record:

- accuracy, macro F1, weighted F1;
- per-action precision, recall, F1 and support;
- confusion matrix;
- prediction distribution;
- valid-action rate;
- ACT prediction count;
- unsafe autonomy / forbidden-ACT count using evaluator-only hard-prohibition metadata;
- counterfactual consistency diagnostic for fully validation-contained relation groups;
- temporal consistency diagnostic for fully validation-contained temporal groups.

No scalar ordinal/intensity action error is defined or reported as a primary metric.

## Determinism and leakage controls

The formal Gate-D run includes:

1. benchmark SHA-256 verification against the Gate-C freeze;
2. automated static boundary scan over baseline source;
3. failure-path tests proving rejection of oracle import, `private.jsonl`, `structured.jsonl`, hard-coded scenario IDs/direct gold tables, and forbidden metadata;
4. canonical validation ordering plus repeated byte-identical inference run;
5. row-order shuffle control;
6. domain ablation diagnostic;
7. observation shuffle diagnostic;
8. development-label permutation control;
9. token-shuffle diagnostic;
10. evaluator recomputation equality check;
11. candidate/private boundary check and output coverage check.

Controls are diagnostics for leakage/shortcut detection. They must not be used to tune B0–B5 after formal validation results are observed.

## Gate-D terminal rules

### PASS

All of the following are required:

- B0–B5 implemented;
- fixed-seed outputs deterministic/byte-identical;
- exactly one valid prediction for every expected validation row;
- valid-action rate = 100%;
- oracle/private/structured/forbidden-metadata baseline boundary violations = 0;
- benchmark SHA mismatch = 0;
- metric recomputation mismatch = 0;
- hidden gold hardcoding/direct scenario-ID lookup = 0;
- all boundary failure-path tests pass;
- frozen `gate_d/freeze_v2.json` and `reports/gate_d_report.json` exist and match the evaluated source/results;
- Python 3.10/3.11/3.12 CI is green.

### BLOCKED

Use **GATE D — BLOCKED** if evidence indicates benchmark leakage/shortcut contamination that undermines Gate-C validity, if frozen benchmark hashes do not match, or if required evidence cannot be obtained without altering frozen upstream artifacts.

### FAIL

Use **GATE D — FAIL** for an unrecoverable methodological failure of the preregistered baseline protocol that does not imply Gate-C benchmark invalidity. Legitimate implementation/infrastructure defects may be fixed and rerun without changing frozen benchmark/spec/oracle or post-hoc success criteria.

## Freeze rule

Formal baseline performance may be computed only after this preregistration commit exists. Gate D is terminal only after source, predictions, controls, metrics, hashes, CI evidence, and preserved failures are frozen. Gate E must not start before Gate-D PASS evidence is frozen.