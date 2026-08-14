# Protocol v2 Claim Boundaries

## Supported now

With Gates B, C, and D passed, current evidence supports narrowly scoped claims that:

- the frozen `PDA-SPEC-v2` is deterministically executable over its bounded valid state space;
- the Gate-C benchmark is reproducibly generated from generator-known state plus the frozen oracle;
- the benchmark has the audited action/rule/prohibition coverage, candidate/private separation, structural diversity, leakage controls, group-aware split integrity, counterfactual integrity, and temporal integrity recorded in `gate_c/freeze_v2.json`;
- future candidate evaluation can be structured to prevent direct runtime reuse of the oracle/private evidence via the Gate-C representation contract;
- Gate D provides a deterministic, leakage-controlled B0–B5 comparison suite and freezes `B5_transparent_heuristic` as the strongest honest raw-context validation baseline at macro-F1 `0.21452991452991452`.

Gate-D PASS is an **integrity** result. It does not imply the baselines are safe, useful, or high-performing.

## Not supported yet

Current evidence does **not** establish:

- candidate performance or superiority;
- candidate safety;
- robustness or adversarial resilience;
- OOD generalization;
- independent protected-set performance;
- human preference alignment;
- that the oracle represents what users generally want;
- universal/objective correctness of the six intervention modes;
- user satisfaction, trust, comfort, psychological validity, or social acceptability;
- ecological validity beyond the modeled/synthetic conditions;
- general personal-assistant quality;
- human consensus or annotation reliability.

## Oracle interpretation

The deterministic oracle is the executable reference implementation of a **research policy**. Agreement means specification compliance, not universal desirability.

## Track-specific boundary

Track A uses structured state and supports mechanistic diagnostics. Track B uses deterministic synthetic semantic observations and supports benchmark evaluation under that generated representation. Track B must not be described as evidence of unrestricted natural-language understanding or real-world contextual proactivity.

## Protected-set boundary

The Gate-C `protected_test` partition is deterministic and publicly regenerable. It is not independent Gate-F protected evidence. Protected-validation credit remains zero until an isolated confirmatory process executes after a Gate-E candidate freeze.

## Historical human validation

Protocol-v1 human-annotation infrastructure remains historical/optional external-validity infrastructure. Protocol v1 itself remains blocked by independent annotation and is not retroactively passed.
