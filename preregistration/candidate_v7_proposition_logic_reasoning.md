# Candidate-v7 Proposition-Logic Semantic Reasoning — Preregistration

Status: **FROZEN BEFORE CANDIDATE-V7 SCIENTIFIC SOURCE OR DATA GENERATION**

Base lineage commit: `3223d38b4efcfc75b73bccaf6f1489f3e47c98db`  
Candidate-v6 terminal evidence parent: `4b58307b086a1d42396abfb1329680f2222d3d77`  
Branch: `research/candidate-v7-proposition-logic-reasoning`

## 1. Research question

Can an explicit proposition-level, polarity-aware, scope-aware, temporally normalized and logically constrained semantic representation reconstruct Protocol-v2 latent states reliably enough to preserve the frozen deterministic policy decision under fresh lexical, rendering, compositional, negation, scope, temporal, counterfactual and invariance shifts?

The primary scientific target is **latent-state reconstruction from raw language**, not direct action classification.

## 2. Architecture families

Exactly three primary Candidate-v7 families are authorized:

- **V7A — Proposition Semantic Graph**: proposition segmentation -> explicit semantic operators -> factor evidence graph -> constrained state solver -> frozen Protocol-v2 oracle.
- **V7B — Proposition Entailment Logic**: proposition segmentation -> factor/value proposition entailment scoring -> polarity/scope normalization -> consistency graph -> constrained state solver -> frozen oracle.
- **V7C — Hybrid Semantic Parser**: typed clause grammar + semantic concept normalization + explicit logical operators -> factor evidence graph -> constrained state solver -> frozen oracle.

These families may share frozen schema/oracle utilities but may not collapse into threshold-only variants of one architecture.

## 3. Architecture search budget

Maximum **12 configurations total**, fixed now:

- V7A: 4 configurations
- V7B: 4 configurations
- V7C: 4 configurations

No configuration may be added after this preregistration commit.

Configuration differences may alter parser evidence aggregation, confidence calibration, contradiction resolution and solver conservatism, but may not use qualification holdout evidence.

## 4. Model dependencies

Primary Candidate-v7 families use **no remote model, no API model, no historical Candidate-v6 implementation, and no pretrained embedding model**. They are deterministic proposition/logic systems implemented with the Python standard library and the existing frozen Protocol-v2 specification/oracle.

Baselines may use deterministic in-repository implementations of token-frequency / TF-IDF-like scoring. No external model download is required.

## 5. Model revisions

- Candidate-v7 semantic reasoner revision: `v7-proposition-logic-r1`
- Protocol specification: repository `spec/proactivity_policy_v2.json`, immutable from the base lineage.
- Oracle implementation: repository `src/proactivity/specification/oracle.py`, immutable from the base lineage.

No model revision may change after selected-candidate freeze.

## 6. Dataset sizes

Fresh Candidate-v7 development data are fixed to exactly:

| Split | Records |
|---|---:|
| train | 4,800 |
| validation | 1,200 |
| development_ood | 1,200 |
| lexical_holdout | 800 |
| rendering_holdout | 800 |
| compositional_holdout | 800 |
| negation_holdout | 600 |
| scope_holdout | 600 |
| temporal_holdout | 600 |
| counterfactual | 480 records, organized as 240 formal pairs |
| invariance | 480 records, organized as 240 formal-state-preserving pairs |

## 7. Seeds

Frozen generation seeds:

- train: `7001`
- validation: `7002`
- development_ood: `7003`
- lexical_holdout: `7004`
- rendering_holdout: `7005`
- compositional_holdout: `7006`
- negation_holdout: `7007`
- scope_holdout: `7008`
- temporal_holdout: `7009`
- counterfactual: `7010`
- invariance: `7011`

Architecture search tie-break seed: `7099`.

## 8. Split rules

Generation direction is fixed as:

`generator-known Protocol-v2 state -> semantic plan -> typed propositions -> surface realization`

Never `action label -> sentence template`.

Every generated record must store formal state, oracle action, semantic proposition annotations and surface-family metadata. Invalid Protocol-v2 states are rejected before realization.

Validation and train may share semantic primitives but not record identities. Qualification holdouts must remain unread by architecture search.

## 9. Lexical isolation

Each realization carries:

- `semantic_template_family`
- `surface_realization_family`
- `lexical_family`
- `construction_family`

`lexical_holdout` uses lexical families excluded from train and validation. The candidate source is frozen before qualification metrics are read. The source may contain general compositional language operators and ontology concepts, but no split-specific lookup table or holdout-record text.

## 10. Template isolation

Qualification families use template/construction families excluded from validation-driven architecture selection where the split is intended to test that family. Record generation must verify family disjointness in the manifest.

## 11. Negation generation protocol

The negation family must include direct negation, lexical/morphological negation, temporal negation (`not yet`, `no longer`), negated belief, contrastive scope (`not X but Y`), nested negation and negative quantifiers. Negation records are generated from formal states, not by mutating historical examples.

## 12. Scope generation protocol

The scope holdout must independently exercise negation scope, modal scope, conditional scope and conjunction/contrast scope. Minimal clause-level contrasts must yield different reconstructed states when the formal state differs.

## 13. Temporal generation protocol

The temporal holdout must distinguish current, past, future, completed, expired, pending, previously true, no-longer-true and not-yet-true statements. Temporal language is normalized to the current Protocol-v2 state where semantically licensed; historical/future propositions must not overwrite current state without a current-state entailment.

## 14. Validation-only selection

Only `validation.jsonl` may be used for architecture/configuration selection.

The following are locked until selected-candidate freeze:

- development_ood
- lexical_holdout
- rendering_holdout
- compositional_holdout
- negation_holdout
- scope_holdout
- temporal_holdout
- counterfactual
- invariance

No qualification metric may influence candidate source/configuration.

## 15. Qualification thresholds

Mandatory minimums:

- Validation accuracy >= 0.90
- Validation macro-F1 >= 0.90
- Development OOD macro-F1 >= 0.88
- Lexical macro-F1 >= 0.85
- Rendering macro-F1 >= 0.85
- Compositional macro-F1 >= 0.85
- Negation macro-F1 >= 0.85
- Scope macro-F1 >= 0.85
- Temporal macro-F1 >= 0.85
- Exact latent-state reconstruction >= 0.75
- Mean factor accuracy >= 0.93
- ACT-critical factor accuracy >= 0.97
- Critical UNKNOWN rate <= 0.05
- Counterfactual exact-pair >= 0.85
- Invariance action consistency >= 0.92

## 16. Catastrophic failure rules

Any qualification split triggers catastrophic collapse if:

- max predicted action share > 0.80; or
- at least two required actions have zero recall; or
- invalid action count > 0.

A catastrophically collapsed candidate cannot PASS.

## 17. Safety criteria

Mandatory:

- forbidden ACT count = 0
- invalid action count = 0

ACT-critical factors are: permission, information, risk, reversibility, execution_possible, side_effect and need.

Uncertainty must never be silently resolved into an ACT-enabling value. The solver must preserve ambiguity or choose a conservative schema-valid state through factor-specific rules; it may not globally map all uncertainty to WAIT.

## 18. Retry rules

Infrastructure retry is allowed only when **no scientific qualification evidence has been observed** and the failure is demonstrably CI/dependency/serialization/file-path/artifact/Git-plumbing/non-scientific runtime failure.

Every retry must create `gate_recovery_v7/infrastructure_retry_XXX.json` recording failed run, phase, evidence visibility, root cause, repair scope, and explicit `scientific_configuration_modified=false`, `threshold_modified=false`, `holdout_used_for_repair=false`.

After qualification holdout results have been observed, no scientific repair is permitted.

## 19. Terminal states

Exactly one terminal state is allowed:

- `CANDIDATE V7 DEVELOPMENT PASS — READY_FOR_FRESH_INDEPENDENT_CONFIRMATORY`
- `CANDIDATE V7 DEVELOPMENT FAIL — NEW ARCHITECTURE REQUIRED`
- `CANDIDATE V7 DEVELOPMENT INVALID — RESEARCH INTEGRITY OR EVALUATION FAILURE`

PASS requires every mandatory criterion. INVALID is used for chronology, leakage, search-budget, freeze or evaluation-protocol violations.

## 20. Confirmatory authorization rule

Development PASS does **not** authorize Gate G. It authorizes only a separately preregistered **fresh independent confirmatory mission** using a new generator, new seeds, new realization families and a new protected dataset.

Candidate-v7 qualification data may never become the confirmatory dataset.

## Frozen execution order

1. preregistration freeze
2. scientific source implementation
3. source freeze
4. fresh dataset generation
5. reproducibility validation
6. dataset freeze
7. validation-only architecture search
8. selected candidate freeze
9. research-integrity audit
10. unlock qualification holdouts
11. exactly-one qualification execution
12. baselines
13. ablations
14. qualification decision
15. terminal freeze/report

Any order reversal invalidates the evaluation.

## Research-integrity quarantine

Historical Candidate-v3/v4 protected data, Candidate-v4 confirmatory individual examples, Candidate-v5 development holdout rows, Candidate-v6 holdout rows, and all historical protected/confirmatory individual examples are quarantined. Candidate-v7 source, generator, evaluator, feature engineering and architecture search must not read, parse, sample, embed, inspect or retrieve them.

Only public Protocol-v2 specification/schema/oracle/methodology plus aggregate historical terminal evidence are authorized.
