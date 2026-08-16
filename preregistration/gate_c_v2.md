# Protocol v2 Gate C preregistration — Oracle and Benchmark Validity

Status at creation: **criteria frozen before formal Gate-C benchmark statistics were inspected**.

Upstream dependency:

- branch: `research/proactivity-specification-v2`
- commit: `89e00052d68b2862269daf2adc8b31ebb1ae592c`
- policy: `PDA-SPEC-v2`
- schema: `2.0.0`
- spec SHA-256: `ea06eeb85ffa375740e778d273b57d79e7f4f96d0eb68eb74ed2ef9df6d827a4`
- oracle source SHA-256: frozen in `gate_c/config_v2.json`

Gate C does not permit changing the normative specification or oracle to improve benchmark balance, coverage, or apparent performance. A specification defect blocks Gate C and requires a new Gate-B cycle.

## Measurement question

Can a benchmark derived from generator-known structured state, the frozen state validator, frozen specification, and deterministic oracle serve as a reproducible, non-circular, leakage-controlled measurement instrument for later baseline/candidate evaluation?

This is not a human-preference or ecological-validity claim.

## Ground-truth provenance

The only accepted decision-label chain is:

`generator-known source state -> frozen validator -> frozen specification -> deterministic oracle -> oracle action + trace`

Manually authored gold actions, LLM-authored gold actions, post-hoc label overrides, and candidate-derived answers are forbidden.

## Representation tracks

### Track A — mechanistic structured-state diagnostics

Candidate transport contains `scenario_id`, `domain`, and structured `state`; the actual model/policy input excludes the transport identifier. Track A is limited to mechanistic rule-compliance and controlled diagnostics.

### Track B — synthetic semantic observation/context

Candidate transport contains `scenario_id`, `domain`, and a deterministic textual `observation`; the actual model/policy input excludes the transport identifier. The observation expresses the source-state semantics without exposing oracle action, rule ID, prohibition trace, relation IDs, template family, split, or answer-bearing metadata.

Track B remains synthetic. Passing it does not justify a broad real-world contextual-proactivity claim.

## Anti-circularity

A future evaluated candidate may not import/call the frozen oracle or read oracle-private benchmark artifacts at runtime. The machine-readable boundary is `gate_c/representation_contract_v2.json`, with `scripts/validate_candidate_boundary_v2.py` reserved for future candidate validation.

## Predeclared blocking criteria

The machine-readable source of truth is `gate_c/config_v2.json`. Structural integrity conditions are zero tolerance for:

- manual gold findings;
- LLM gold dependencies;
- oracle mismatches;
- forbidden candidate-visible answer metadata;
- exact candidate-record duplication;
- accidental structured-state duplication;
- relation-family split leakage;
- candidate/private forbidden-field overlap;
- counterfactual or temporal relation violations.

Coverage minima were frozen before the formal audit:

- at least 6 benchmark examples for every selection rule that is reachable as the selected non-fallback decision;
- at least 12 examples for each of the six actions;
- at least 6 trigger examples for every hard prohibition;
- at least one single-variable action-changing prohibition counterfactual per hard prohibition;
- at least 8 generic action-changing counterfactual families;
- at least 6 temporal sequences;
- largest observation-template-family share at most 0.34.

These thresholds are benchmark-validity sampling requirements, not claims about natural action prevalence. Natural exhaustive action distribution and benchmark sampling distribution must be reported separately.

## Split policy

Family-aware split assignment keeps members of a counterfactual family, temporal sequence, or state family together. Random row splitting is forbidden.

Gate C may materialize a deterministic public `protected_test` holdout to validate freeze and split mechanics. Because the generator is public and reproducible, this public holdout is **not** independent Gate-F protected evidence. A truly confirmatory protected test requires access/process isolation defined in `gate_c/protected_test_protocol_v2.json`.

## Leakage diagnostics

Gate C audits:

- candidate-visible forbidden fields and direct action tokens;
- identifier-prefix predictability;
- row-position bucket predictability;
- domain-only predictability;
- template-family-only predictability;
- label-conditional lexical purity;
- relation-family split leakage.

The simple predictors above are leakage diagnostics only. They are not Gate-D formal baselines and must not be reported as baseline evidence.

High-purity lexical features are not automatically leakage: semantic evidence can legitimately correlate with the oracle action. Direct answer tokens or answer-bearing generator metadata are forbidden; other high-purity tokens are reported for interpretation as potential generator shortcuts.

## Reproducibility

CI must regenerate Gate-C artifacts twice and require byte-identical outputs, then generate the formal artifact set and machine-readable Gate-C report. Python 3.10, 3.11, and 3.12 remain in the matrix.

## Verdict rule

Only these outcomes are allowed:

- `GATE C — PASS`
- `GATE C — BLOCKED: <exact reason>`
- `GATE C — FAIL: <exact reason>`

A PASS requires every preregistered blocking criterion to pass. No `PARTIAL PASS`, `MOSTLY PASS`, or post-hoc threshold relaxation is allowed.

Even after PASS, Gate D must not execute in this mission.
