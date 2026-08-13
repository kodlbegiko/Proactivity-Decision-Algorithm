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
