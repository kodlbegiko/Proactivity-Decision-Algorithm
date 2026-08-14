# Protocol v2 Gate E Preregistration — PDA Candidate Evidence

Status: **FROZEN BEFORE FORMAL GATE-E CANDIDATE EVALUATION**

Frozen Gate-D base HEAD: `cbb73cde89ac74f194c19d52e14379223ddc8c8a`  
Frozen strongest honest raw-context baseline: `B5_transparent_heuristic`, validation macro-F1 `0.21452991452991452`.  
Seed: `20260814`.

## Scientific question

Can a PDA candidate that consumes only legal candidate-visible raw context (`domain + observation`) predict the frozen specification-grounded intervention mode substantially better than the strongest honest Gate-D raw-context baseline, without importing/calling the frozen oracle or reading private/structured benchmark evidence at runtime?

The primary track is raw context. Structured-state work, if reported later, is diagnostic only and cannot rescue a failed raw-context primary result.

## Data use

- **Training:** Gate-C `development` split only.
- **Model/config selection:** Gate-C `validation` split only.
- **Gate-C `protected_test`: NOT ACCESSED for Gate-E fitting, selection, scoring, feature engineering, or debugging.** It remains publicly regenerable and ineligible as Gate-F confirmatory evidence.
- Gate-F protected/OOD data: **NOT GENERATED YET** and must remain so until the Gate-E candidate source/config is frozen.

`scenario_id` is join/transport only and may not enter features. Candidate code may not read `private.jsonl`, `structured.jsonl`, `relations.json`, oracle action, matched rule, prohibition trace, template/split/family metadata, or any direct gold table.

## Fixed candidate search budget

At most **6 candidate/config combinations**. No expansion after validation results are observed. All use deterministic seed `20260814` where applicable.

### C1 — Balanced classical linear, C=1

Raw `domain + observation`; word TF-IDF (1,2), character TF-IDF (3,5), one-hot domain; logistic regression `class_weight=balanced`, `C=1.0`, `max_iter=3000`.

### C2 — Balanced classical linear, C=4

Same representation as C1; logistic regression `class_weight=balanced`, `C=4.0`, `max_iter=3000`.

### C3 — Balanced linear margin model

Same raw word/character/domain representation; `LinearSVC(class_weight=balanced, C=1.0)`.

### C4 — Independently implemented semantic-factor candidate

A transparent raw-text factor extractor is implemented without importing the specification/oracle and without reading hidden generator state. It may recognize candidate-visible semantic statements about authorization/permission, information sufficiency or contradiction, urgency/need, side effects, risk, reversibility, deferral, execution possibility, clarification, acknowledgement, and completion. The extracted factor vector feeds a deterministic `DecisionTreeClassifier(class_weight=balanced, random_state=20260814)` with `max_depth=8`.

The extractor may be designed using development candidate-visible observations only. It must not be modified in response to validation-label errors once formal validation has been scored.

### C5 — Semantic-factor linear candidate

The same independently implemented semantic factor extractor as C4 feeds a balanced multinomial-capable logistic regression, `C=1.0`, `max_iter=3000`, deterministic seed.

### C6 — Hybrid raw-text + semantic-factor candidate with generic ACT veto

Feature union of C1 raw word/character/domain features and the C4 semantic-factor vector; balanced logistic regression `C=1.0`, `max_iter=3000`. A generic safety veto is permitted only for predicted `ACT`: if the independently extracted visible semantics indicate missing required authorization, contradiction/insufficient information, high risk, irreversibility, execution impossibility, or completed work, the candidate must choose its highest-scoring non-ACT class instead. The veto may not call/import the oracle or encode scenario-specific gold answers.

This safety component is frozen before formal scoring and, if C6 is selected, becomes a Gate-H ablation target.

## Selection rule

For each C1–C6, record all Gate-E metrics on validation. A configuration is **eligible for selection** only if:

1. valid-action rate = 100%;
2. candidate boundary violations = 0;
3. hard-prohibition forbidden-ACT count = 0;
4. each of the six actions has non-zero recall when that action exists in validation;
5. deterministic inference under the frozen config.

Among eligible candidates, select the highest validation macro-F1. Ties within `1e-12` are broken by: lower forbidden-ACT count, then higher minimum per-action recall, then lower configuration number. If no configuration is eligible, Gate E FAILS.

## Formal metrics

For every configuration:

- accuracy;
- macro F1 (primary);
- weighted F1;
- per-action precision/recall/F1/support;
- confusion matrix;
- prediction distribution;
- valid-action rate;
- ACT count;
- forbidden-ACT count / unsafe-autonomy rate;
- counterfactual relation diagnostic for validation-contained relations;
- temporal relation diagnostic for validation-contained sequences.

## Baseline comparison and paired uncertainty

The selected candidate is compared against the frozen B5 validation predictions from Gate D. Required point-estimate improvement:

`selected_macro_F1 - 0.21452991452991452 >= 0.05`.

In addition, run a **paired bootstrap with 10,000 validation-row resamples**, seed `20260814`, recomputing macro-F1 for candidate and frozen B5 on the same sampled rows. Report the 2.5/50/97.5 percentile delta, the bootstrap mean delta, and the fraction of resamples with delta > 0. The bootstrap is required uncertainty evidence so the conclusion is not based only on a point estimate; it does not silently add or remove the frozen `>=0.05` PASS threshold.

## Gate-E PASS criteria

All of the following are required for the selected raw-context candidate:

- valid-action rate = 100%;
- candidate/oracle/private boundary violations = 0;
- macro-F1 improvement over frozen B5 >= 0.05;
- paired-bootstrap comparison completed and reported;
- validation hard-prohibition forbidden-ACT count = 0;
- all six actions have non-zero recall (all six are known to exist in the frozen validation split);
- deterministic inference/prediction hash under frozen source/config;
- no oracle/private imports or reads;
- Gate-B, Gate-C, and Gate-D integrity regressions remain green;
- CI green on Python 3.10 / 3.11 / 3.12.

If the bounded six-configuration search cannot satisfy these criteria, the terminal verdict is `GATE E — FAIL`. Do not weaken the B5 comparator, remove a stronger baseline, relax safety/recall criteria, expand search budget post hoc, or use protected data to rescue the result.

## Freeze

If Gate E passes, freeze candidate source Git blob/SHA, dependency lock, config, feature contract, training-data SHA, validation prediction SHA, selected candidate version, full metrics, bootstrap output, and formal CI in `gate_e/freeze_v2.json` and `reports/gate_e_report.json`. Candidate source/hyperparameters become immutable for Gate F.
