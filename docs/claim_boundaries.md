# Protocol v2 Claim Boundaries

## Supported now

With Gates B, C, D, and formal-source Gate E passed, current evidence supports narrowly scoped claims that:

- the frozen `PDA-SPEC-v2` is deterministically executable over its bounded valid state space;
- the Gate-C benchmark is reproducibly generated from generator-known state plus the frozen oracle;
- the benchmark has the audited action/rule/prohibition coverage, candidate/private separation, structural diversity, leakage controls, group-aware split integrity, counterfactual integrity, and temporal integrity recorded in `gate_c/freeze_v2.json`;
- future candidate evaluation can be structured to prevent direct runtime reuse of the oracle/private evidence via the Gate-C representation contract;
- Gate D provides a deterministic, leakage-controlled B0–B5 comparison suite and freezes `B5_transparent_heuristic` as the strongest honest raw-context validation baseline at macro-F1 `0.21452991452991452`;
- under the frozen validation split and controlled synthetic raw-observation representation, the preregistered selected `C5_semantic_factor_linear` candidate achieved macro-F1 `0.6936507936507935`, delta `+0.479120879120879` over B5, 100% valid actions, zero forbidden ACT, and non-zero recall for all six actions;
- the preregistered 10,000-resample paired bootstrap produced a positive macro-F1 delta interval `[0.269140495727183, 0.6969364243570899]`, with fraction delta > 0 equal to `1.0`;
- the formal Gate-E results were byte-identical across Python 3.10/3.11/3.12 and the candidate source was frozen before formal validation.

Gate-D PASS remains an **integrity** result. Gate-E PASS is a **validation** result under the controlled synthetic representation. Neither establishes universal desirability or real-world generalization.

## Not supported yet

Current evidence does **not** establish:

- independent protected/OOD generalization;
- robustness or adversarial resilience;
- production readiness or proven safety;
- real-world contextual understanding or ecological validity beyond the modeled/synthetic conditions;
- human preference alignment;
- that the oracle represents what users generally want;
- universal/objective correctness of the six intervention modes;
- user satisfaction, trust, comfort, psychological validity, or social acceptability;
- general personal-assistant quality or SOTA status;
- human consensus, annotation reliability, or independent human replication.

## Oracle interpretation

The deterministic oracle is the executable reference implementation of a **research policy**. Agreement means specification compliance, not universal desirability.

## Track-specific boundary

Track A uses structured state and supports mechanistic diagnostics. Track B uses deterministic synthetic semantic observations and supports benchmark evaluation under that generated representation. The selected C5 candidate operates on Track-B observation semantics through its independently implemented visible-semantic factor extractor. This must not be described as evidence of unrestricted natural-language understanding or real-world contextual proactivity.

## Protected-set boundary

The Gate-C `protected_test` partition is deterministic and publicly regenerable. It is not independent Gate-F protected evidence. During Gate E, protected candidate/private payload rows were skipped without JSON parsing. Protected-validation credit remains zero until a new chronological/process-isolated Gate-F confirmatory set is generated after the Gate-E candidate freeze and evaluated once under preregistered criteria.

## Historical human validation

Protocol-v1 human-annotation infrastructure remains historical/optional external-validity infrastructure. Protocol v1 itself remains blocked by independent annotation and is not retroactively passed.
