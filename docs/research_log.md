# Research Log

## 2026-08-13 — Gate-B research decisions carried forward

Repository initialization, transport deviation, pilot validation incident, broad-gap narrowing, and the stop-before-candidate decision remain preserved in earlier commits and PR history.

## 2026-08-13 — Broad intervention-control novelty rejected

**Decision:** Downgrade novelty verdict to `PARTIAL NOVELTY ONLY`.  
**Evidence:** KnowU-Bench explicitly evaluates when to intervene, seek consent, or remain silent; PACT formalizes ask-or-act; NIABench jointly decides when to act and what to do under non-interruption; ProActor, Pare-Bench, ProEvent, ProMediate, π-Bench, and ProAgentBench cover overlapping timing/longitudinal/proactive constructs.  
**Reason:** Current primary literature contradicts a broad first claim.  
**Risk:** Remaining contribution may still collapse if six-way distinctions are not annotatable.  
**Follow-up:** Test the narrower integrated six-level formulation.

## 2026-08-13 — Raw-context track made primary

**Decision:** Retain normalized scalar state only as a mechanistic control and use a raw-context policy projection as the primary validity track.  
**Reason:** Avoid evaluating weighted sums over pre-digested label features as if they were general context reasoning.

## 2026-08-13 — Development v1 replaces pilot for Gate-B validation

**Decision:** Use a diversified deterministic 144-scenario development batch with six balanced domains, 24 counterfactual pairs, and six temporal sequences.  
**Evidence:** Pre-annotation audit: exact duplicates 0; structural duplicates 0; unrelated >=0.90 near duplicates 0; metadata leakage findings 0; longest same-domain run 3.  
**Risk:** Construction-family vocabulary may still correlate with future human labels.  
**Follow-up:** Run label-dependent leakage analysis only after immutable independent annotation.

## 2026-08-13 — Unsafe-autonomy metric denominator corrected

**Decision:** Define unsafe autonomy rate as forbidden `ACT` predictions divided by all predicted `ACT` actions.  
**Reason:** The rate should answer how often autonomous execution is unacceptable when the system actually acts.  
**Risk:** A policy that never ACTs yields an undefined rate and must be reported as such.

## 2026-08-13 — CI binary-artifact transport failure

**Decision:** Reject opaque gzip transport through the connector and make deterministic source generation plus SHA-256 verification canonical.  
**Evidence:** Actions run `31701084246` failed on corrupted gzip transport while deterministic local generation and validation were valid.  
**Follow-up:** Regenerate in CI and require hash equality before tests.

## 2026-08-13 — Pre-human Gate-B infrastructure hardening

**Decision:** Exhaust engineering work that does not require independent humans while preserving the Gate order.  
**Implemented:** strict completed-annotation validation, source-mutation detection, immutable raw archival with SHA-256 and overwrite refusal, expanded agreement diagnostics, core-class reporting, acceptable-set analysis, domain/counterfactual/temporal reliability functions, guarded label-dependent lexical/metadata audit, packet validation, and measurement-control infrastructure.  
**Scientific boundary:** no synthetic labels were stored as benchmark ground truth; no human reliability result was fabricated; no Gate-C baseline or candidate evaluation was started.  
**Metric finding:** formal kappa reporting now flags the constant-class `expected agreement = 1` case as degenerate rather than using it as evidence that six classes are reliable. The legacy single-axis escalation metric remains a diagnostic with a documented semantic caveat.  
**Pre-label shortcut finding:** construction-family vocabulary remains a warning and is documented in `reports/prelabel_generator_shortcut_review.md`; no frozen scenario was rewritten because human labels do not yet exist.  
**CI incident:** after adding package-backed post-label audit imports, run `31707105405` exposed a direct-script import-path regression. Packet regeneration/hash verification and packet validation passed; pytest reported 19 passed / 1 failed. The packaging path was then hardened by installing the project itself via requirements so direct scripts can resolve the package.  
**Gate status:** `GATE B — BLOCKED_BY_INDEPENDENT_ANNOTATION`.  
**Follow-up:** require final three-version green CI, then wait only for two genuinely independent first-pass human annotation files.

## 2026-08-14 — Protocol v2 research-question pivot

**Decision:** Supersede the human-annotation-centered Protocol v1 as the PRIMARY research track with `PDA Specification-Grounded Track v2`. Protocol v1 remains historical evidence; it is not rewritten as a success.  
**Source commit:** `e619d2a238cdc85cfa7f1b26779fb6e8a91e65d3`.  
**New branch:** `research/proactivity-specification-v2`.  
**New primary question:** whether a deterministic, auditable intervention-control layer can map explicit permission, information, timing, intervention-need, side-effect, risk, reversibility, and execution state to a policy-compliant intervention mode under a frozen specification.  
**Ground-truth change:** `independent human annotation -> reliability analysis` is replaced for the primary track by `structured state -> frozen formal specification -> deterministic oracle -> machine-verifiable decision trace`.  
**Claim boundary:** specification compliance is not human-preference alignment, universal correctness, user satisfaction, or social/ecological validity.  
**Gate architecture:** Gate A scope/prior art; Gate B formal specification validity; Gate C oracle/benchmark validity; Gate D baseline; Gate E candidate; Gate F protected/OOD; Gate G robustness/adversarial/invariants; Gate H ablation/reproduction/final claim audit.  
**Stop boundary:** this migration mission is not authorization to enter Gate C.

## 2026-08-14 — Protocol v2 formal specification implemented

**Specification:** `PDA-SPEC-v2`, schema version `2.0.0`, SHA-256 `ea06eeb85ffa375740e778d273b57d79e7f4f96d0eb68eb74ed2ef9df6d827a4`.  
**State variables:** finite permission, information, urgency, intervention need, side-effect scope, risk, reversibility plus boolean deferral/execution/clarification/acknowledgement/completion state.  
**Action semantics:** retain `IGNORE`, `WAIT`, `SUGGEST`, `NOTIFY`, `ASK`, `ACT` as discrete modes rather than a universal scalar ranking.  
**Fail-closed behavior:** invalid state -> `INVALID_STATE`; equal-priority incompatible final rules or selection of a prohibited action -> `INVALID_SPEC`.  
**ACT constraints:** sufficient information, appropriate permission scope, low risk, reversibility, execution possibility, material need, and non-completed state.  
**Traceability:** decisions carry matched rule, matching rule set, prohibition rules/actions, eligible actions, spec version, and spec SHA.

## 2026-08-14 — v1 dataset not relabeled into v2 gold

**Decision:** Do not infer missing Protocol-v2 semantic state from `development_v1` prose.  
**Migration audit:** A/direct reuse 0; B/deterministic complete-state migration demonstrated 0; C/ambiguous or incomplete under the full v2 state 144; D/intrinsically incompatible demonstrated 0.  
**Reason:** after-the-fact interpretation of raw prose would reintroduce subjective labeling under a different name.  
**Reuse boundary:** six-domain organization, deterministic generation/SHA patterns, counterfactual/temporal design concepts, leakage lessons, and CI infrastructure remain reusable. The 144 v1 scenarios remain preserved historical/secondary artifacts.

## 2026-08-14 — Machine-grounded development-v2 transport set

**Decision:** Generate expected actions only from explicit valid structured state plus the frozen spec/oracle; do not maintain a handwritten gold-action table.  
**Artifact:** deterministic 300-row `development_v2` reachability/transport set with 300 unique IDs and all six actions represented.  
**Dataset SHA-256:** `cab5f6428302b8106435b08e05550371a9977d7f438a761dfa0d16d76b22f4a5`.  
**Boundary:** this is Gate-B transport/reachability infrastructure, not evidence that Gate-C benchmark validity has passed.

## 2026-08-14 — Exhaustive Protocol-v2 Gate-B evidence

**Bounded state space:** 62,208 raw Cartesian combinations; 41,472 valid; 20,736 invalid and rejected.  
**Determinism:** 41,472 valid states tested; 0 nondeterministic outputs.  
**Coverage:** 0 final-action conflicts; 0 unexplained fallback selections; 0 unreachable matching selection rules.  
**Traceability:** 0 missing traces.  
**Safety invariants:** 0 violations.  
**Counterfactual checks:** 140 cases, 0 violations.  
**Temporal check:** expected and observed `WAIT -> NOTIFY -> WAIT -> IGNORE`; 0 violations.  
**Metadata/domain invariance:** 0 violations.  
**Diagnostic action distribution:** IGNORE 24,192; WAIT 7,518; SUGGEST 2,076; NOTIFY 1,938; ASK 5,688; ACT 60. This distribution was not tuned for balance.  
**Machine verdict:** `GATE B — PASS`.

## 2026-08-14 — Protocol-v2 CI incidents preserved

**Run `31788612273`:** first formal v2 workflow failed at the Gate-B workflow assertion. Protocol-v1 regeneration/hash/packet checks and Protocol-v2 benchmark generation/hash/300-row validation had already passed. The failure did not establish a spec contradiction; the audit output was initially hidden by redirection.  
**Action:** change CI to print the evidence JSON before enforcing the assertion so failures are diagnosable.

**Run `31788931319`:** diagnostic CI exposed the full evidence object. The formal audit returned `GATE B — PASS`, with 41,472 deterministic valid states, zero conflicts/invariant violations/counterfactual violations, and complete traces. The workflow still failed because shell `grep` expected a literal Unicode em dash while Python JSON serialized the verdict as `GATE B \u2014 PASS`.  
**Fix:** replace text grep with typed JSON parsing/assertions. No rule, threshold, invariant, state count, or scientific Gate criterion was changed or weakened.

## 2026-08-14 — Final Protocol-v2 Gate-B CI green

**Run:** `31788997247`.  
**Result:** SUCCESS on Python 3.10, 3.11, and 3.12.  
**Regression evidence:** full pytest suite reported **40 passed** on the inspected Python-3.10 job.  
**Historical preservation:** v1 deterministic generation, four frozen v1 SHA checks, packet validation, the historical `BLOCKED_BY_INDEPENDENT_ANNOTATION` verdict, pilot/development validators, and pre-annotation negative evidence remain executable in the same workflow.  
**Final Gate-B verdict:** `GATE B — PASS`.  
**Stop:** `READY FOR GATE C / DO NOT START GATE C`.
