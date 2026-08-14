# Gate Status — 2026-08-14 — Protocol v2

## Historical Protocol v1

Protocol v1 remains preserved as historical evidence. Its last scientific state was:

- Gate A: `PASS (narrowed)`;
- Gate B: `BLOCKED_BY_INDEPENDENT_ANNOTATION`;
- evidence-weighted completion: **25%** under the v1 weighting;
- genuinely independent human annotation: **NOT EXECUTED**;
- raw agreement / Cohen's kappa / human-label-dependent leakage checks: **NOT EXECUTED**.

Protocol v2 does not retroactively convert those missing results into passes. The project changed its primary research question and ground-truth definition.

## Protocol v2 primary track

### Gate A — Scope / claim boundary / prior-art positioning: PASS (narrowed)

The primary research target is now **specification-grounded intervention control**. The frozen specification is a research policy, not universal human truth. Protocol v2 may evaluate specification compliance, permission-sensitive autonomy, constraint satisfaction, traceability, counterfactual/temporal consistency, and later robustness/OOD behavior. It must not claim human-preference alignment, user satisfaction, universal correctness, or ecological validity beyond the modeled conditions.

The novelty verdict remains **PARTIAL NOVELTY ONLY**. Constrained policies, shielding/action filtering, proactive intervention timing, ask/act trade-offs, and permission/capability separation all have prior art. Any later contribution must therefore be supported at the integrated formulation/evaluation/evidence level rather than by terminology alone.

### Gate B — Formal Specification Validity: PASS

Machine-generated verdict:

```text
GATE B — PASS
READY FOR GATE C
DO NOT START GATE C
```

#### Frozen specification

- policy: `PDA-SPEC-v2`;
- schema version: `2.0.0`;
- specification SHA-256: `ea06eeb85ffa375740e778d273b57d79e7f4f96d0eb68eb74ed2ef9df6d827a4`;
- six discrete intervention-control modes: `IGNORE`, `WAIT`, `SUGGEST`, `NOTIFY`, `ASK`, `ACT`;
- no universal scalar ordering is assumed;
- invalid states fail closed rather than being coerced to one of the six actions.

#### Exhaustive bounded-state evidence

- raw Cartesian combinations: **62,208**;
- valid states: **41,472**;
- invalid states rejected: **20,736**;
- deterministic states tested: **41,472**;
- nondeterministic outputs: **0**;
- equal-priority/final-action conflicts: **0**;
- unexplained fallback selections: **0**;
- unreachable matching selection rules: **0**;
- trace-missing valid decisions: **0**;
- mandatory invariant violations: **0**;
- metadata/domain invariance violations: **0**.

Action distribution is diagnostic only and was not optimized for balance:

| Action | Exhaustive valid-state count |
|---|---:|
| IGNORE | 24,192 |
| WAIT | 7,518 |
| SUGGEST | 2,076 |
| NOTIFY | 1,938 |
| ASK | 5,688 |
| ACT | 60 |

#### Structural relation tests

- counterfactual cases: **140**;
- counterfactual violations: **0**;
- temporal reference sequence: `WAIT -> NOTIFY -> WAIT -> IGNORE`;
- temporal violations: **0**;
- ACT constraints cover information sufficiency, permission scope, low risk, reversibility, execution possibility, material need, and completion state;
- scenario/domain identifiers and row ordering are not normative oracle inputs.

#### Protocol-v2 development transport artifact

- deterministic generated rows: **300**;
- unique IDs: **300**;
- all six actions represented;
- dataset SHA-256: `cab5f6428302b8106435b08e05550371a9977d7f438a761dfa0d16d76b22f4a5`;
- every expected action is recomputed from the frozen state + frozen specification; there is no separate hand-written gold-label table.

This artifact proves deterministic transport/reachability infrastructure at Gate B. It does **not** by itself establish Gate-C benchmark validity.

#### Dataset migration audit

The historical `development_v1` set was not silently relabeled. Classification of its 144 scenarios under the complete Protocol-v2 semantic state:

- A — directly reusable as v2 formal evidence: **0**;
- B — demonstrably recoverable by deterministic complete-state migration: **0**;
- C — incomplete/ambiguous under the full v2 state and therefore not assigned v2 gold: **144**;
- D — intrinsically incompatible: **0 demonstrated**.

The v1 scenarios and their negative evidence remain preserved for historical/secondary use.

#### CI / test evidence

Final validation run: **GitHub Actions `31788997247` — SUCCESS**.

- Python 3.10: SUCCESS;
- Python 3.11: SUCCESS;
- Python 3.12: SUCCESS;
- full pytest suite: **40 passed** on the inspected 3.10 matrix job;
- Protocol-v1 generation, frozen SHA verification, packet validation, blocked historical verdict, and dataset validators remain green in the same workflow;
- no human annotation files were fabricated or introduced.

#### Preserved Protocol-v2 CI incidents

1. Run `31788612273` failed at the Gate-B workflow assertion after v1 checks and v2 benchmark hash/row validation had passed. The later diagnostic run established that the formal audit itself returned `GATE B — PASS`; the failure was a fragile shell text assertion.
2. Run `31788931319` surfaced the complete Gate-B JSON: the verdict was `GATE B — PASS`, but a `grep` expected a literal Unicode em dash while JSON serialized it as `\u2014`. The workflow was repaired by parsing JSON and asserting typed fields. No specification rule, threshold, invariant, state count, or Gate criterion was weakened to obtain the final green run.

## Gate C — Oracle and Benchmark Validity

**NOT EXECUTED — BLOCKED BY GATE ORDER / EXPLICIT TASK BOUNDARY.**

Gate B PASS authorizes the next research task but this mission stops before Gate C. No formal benchmark-validity claim, baseline ranking, candidate tuning, protected-set evaluation, or candidate-performance result has been executed.

## Gates D–H

**NOT EXECUTED.**

No baseline integrity result, PDA candidate result, protected/OOD result, robustness claim, ablation claim, independent reproduction result, merge, or release has been executed.

## Protocol-v2 evidence-weighted completion

Weights are frozen for this Protocol-v2 status report before later candidate results exist:

| Evidence area | Weight | Supported now |
|---|---:|---:|
| Research scope / claim definition | 10% | 10% |
| Formal specification validity | 20% | 20% |
| Oracle / benchmark validity | 15% | 0% |
| Baseline integrity | 15% | 0% |
| Candidate evidence | 15% | 0% |
| Protected validation | 10% | 0% |
| Robustness | 5% | 0% |
| Ablation | 5% | 0% |
| Reproducibility / independent reproduction | 5% | 3% |
| **Total** | **100%** | **33%** |

The 3/5 reproducibility credit reflects deterministic generators, frozen SHA manifests, and successful Python 3.10/3.11/3.12 CI. The remaining 2/5 is withheld because an independent clean-environment reproduction/audit has not been performed. Gate-C infrastructure volume receives no scientific completion credit before Gate C actually executes.

## Exact next scientifically valid action

Run **Gate C — Oracle and Benchmark Validity** as a separate mission. It should validate that the oracle-derived benchmark is non-circular, structurally diverse, leakage-resistant, domain-balanced only where scientifically justified, counterfactually/temporally well-formed, and suitable for freezing before any formal baseline or PDA candidate comparison.

Do not begin baseline ranking or candidate optimization until Gate C passes.
