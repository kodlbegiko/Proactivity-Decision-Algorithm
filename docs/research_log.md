# Research Log

## 2026-08-13 — Gate-B research decisions carried forward

Repository initialization, transport deviation, pilot validation incident, broad-gap narrowing, and the stop-before-candidate decision remain preserved in earlier commits and PR history.

## 2026-08-13 — Broad intervention-control novelty rejected

**Decision:** Downgrade novelty verdict to `PARTIAL NOVELTY ONLY`.  
**Evidence:** KnowU-Bench explicitly evaluates when to intervene, seek consent, or remain silent; PACT formalizes ask-or-act; NIABench jointly decides when to act and what to do under non-interruption; ProActor, Pare-Bench, ProEvent, ProMediate, π-Bench, and ProAgentBench cover overlapping timing/longitudinal/proactive constructs.  
**Alternatives:** Continue claiming a first benchmark for intervention/silence/permission.  
**Reason:** Current primary literature contradicts that claim.  
**Risk:** Remaining contribution may still collapse if six-way distinctions are not annotatable or a closer equivalent is found.  
**Reversible?:** Only with materially stronger evidence.  
**Follow-up:** Test the narrower integrated six-level cost-sensitive formulation.

## 2026-08-13 — Raw-context track made primary

**Decision:** Retain normalized scalar state only as a mechanistic control and introduce a raw-context policy projection as the primary validity track.  
**Evidence:** Existing schema directly supplied importance, urgency, interruptibility, action risk, and expected delay cost, which can encode researcher judgment close to the decision target.  
**Alternatives:** Use scalar state as the only benchmark input.  
**Reason:** Avoid evaluating weighted sums over pre-digested label features as if they were general context reasoning.  
**Risk:** Raw-context evaluation adds inference difficulty.  
**Reversible?:** Yes; both tracks are retained.  
**Follow-up:** Freeze track roles before protected evaluation.

## 2026-08-13 — Development v1 replaces pilot for Gate-B validation

**Decision:** Build a diversified 144-scenario development batch with six balanced domains, 24 counterfactual pairs, and six temporal sequences.  
**Evidence:** Executed pre-annotation audit after deterministic regeneration: exact duplicate members 0; structural duplicates 0; unrelated >=0.90 near duplicates 0; metadata leakage findings 0; longest same-domain run 3.  
**Alternatives:** Repair and expand pilot-v0 templates.  
**Reason:** Pilot-v0 structure was fundamentally duplicated and unsuitable for formal ranking.  
**Risk:** Synthetic v1 may still contain lexical shortcuts correlated with future human labels. Construction-family vocabulary is explicitly flagged for post-label testing.  
**Reversible?:** Yes, development data may be revised before freeze.  
**Follow-up:** Run label-dependent leakage analysis after independent annotation.

## 2026-08-13 — Unsafe-autonomy metric denominator corrected

**Decision:** Define unsafe autonomy rate as forbidden `ACT` predictions divided by all predicted `ACT` actions.  
**Evidence:** A toy test exposed that dividing by all scenarios where ACT was forbidden diluted one unsafe autonomous action from 1/1 to 1/2.  
**Alternatives:** Divide by all scenarios or all ACT-forbidden scenarios.  
**Reason:** The rate should answer: when the system autonomously acts, how often is that autonomy unacceptable?  
**Risk:** A policy that never ACTs yields undefined rate and must be reported with action coverage.  
**Reversible?:** Yes, before metric freeze.  
**Follow-up:** Preserve explicit denominators in metric documentation.

## 2026-08-13 — CI binary-artifact transport failure

**Decision:** Reject opaque gzip transport through the connector and make deterministic source generation plus SHA-256 verification the canonical artifact path.  
**Evidence:** GitHub Actions run `31701084246` failed before tests at `gzip -dk data/development/development_v1.jsonl.gz` with `invalid compressed data--format violated`, while local uncompressed generation, hash checks, validation, audit, and tests were valid.  
**Alternatives:** Re-upload the same opaque binaries and retry until green.  
**Reason:** Repeated opaque transport would make reproducibility dependent on a flaky connector path and could hide corruption.  
**Risk:** Generated artifacts are materialized on demand rather than stored directly as large binary blobs.  
**Reversible?:** Yes.  
**Follow-up:** Commit the readable deterministic generator and expected hashes; regenerate on CI and require hash equality before tests.
