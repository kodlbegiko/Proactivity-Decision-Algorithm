# Research Log

## 2026-08-13 — Repository initialization

**Decision:** Keep `main` minimal and move substantive work to `research/proactivity-decision-v0`.  
**Evidence:** Repository metadata reported size 0 and commit listing returned `Git Repository is empty`.  
**Alternatives:** Build directly on `main`.  
**Reason:** Preserve a stable entry branch and clean research evidence trail.  
**Risk:** Minimal bootstrap commit on `main` precedes full research structure.  
**Reversible?:** Yes.  
**Follow-up:** Open a draft PR from the research branch.

## 2026-08-13 — Clone infrastructure deviation

**Decision:** Use the GitHub connector/API for remote writes rather than local network git.  
**Evidence:** Sandbox `git clone` failed because `github.com` DNS could not resolve; the GitHub connector retained admin/push access.  
**Alternatives:** Stop all research work.  
**Reason:** Transport failure does not prevent repository inspection, branch control, commits, or evidence preservation through the connector.  
**Risk:** Local git command provenance is unavailable for initialization.  
**Reversible?:** Yes.  
**Follow-up:** Preserve exact remote SHAs and local test outputs.

## 2026-08-13 — Research gap narrowed

**Decision:** Reject the broad claim that proactive-agent benchmarks are absent. Test a narrower intervention-control contribution.  
**Evidence:** ProactiveEval, ProActor, π-Bench, Pare-Bench, ProAgentBench and NIABench materially overlap with proactive evaluation/timing.  
**Alternatives:** Continue with a generic “proactive assistant benchmark.”  
**Reason:** That would be poorly differentiated.  
**Risk:** A deeper review may find an equivalent formulation.  
**Reversible?:** Yes; negative novelty is valid.  
**Follow-up:** Complete systematic comparison.

## 2026-08-13 — Stop before candidate development

**Decision:** Build measurement infrastructure but do not tune a substantive candidate.  
**Evidence:** No independent annotation agreement has been measured.  
**Alternatives:** Generate labels from one researcher and optimize immediately.  
**Reason:** That risks measuring researcher self-consistency rather than proactive decision quality.  
**Risk:** Slower visible progress, stronger validity.  
**Reversible?:** Candidate work begins once gates pass.  
**Follow-up:** Obtain independent labels.

## 2026-08-13 — Local validation incident

**Decision:** Treat the first dataset validation failure as real evidence, fix the malformed timestamp, then rerun checks.  
**Evidence:** Initial validator rejected `2026-08-15T010:00:00Z`; after correction the pilot validated and pytest passed.  
**Alternatives:** Ignore because unit tests passed.  
**Reason:** Dataset validity is independent evidence.  
**Risk:** Generator needed stronger regression coverage.  
**Reversible?:** Yes.  
**Follow-up:** Keep dataset validation in CI.

## 2026-08-13 — Broad intervention-control novelty rejected

**Decision:** Downgrade novelty verdict to `PARTIAL NOVELTY ONLY`.  
**Evidence:** KnowU-Bench explicitly evaluates when to intervene, seek consent, or remain silent; PACT formalizes ask-or-act; NIABench jointly decides when to act and what to do under non-interruption; ProActor, Pare-Bench, ProEvent, ProMediate, π-Bench, and ProAgentBench cover overlapping timing/longitudinal/proactive constructs.  
**Alternatives:** Continue claiming a first benchmark for intervention/silence/permission.  
**Reason:** Current primary literature contradicts that claim.  
**Risk:** Remaining contribution may still collapse if six-way distinctions are not annotatable or if a closer equivalent is found.  
**Reversible?:** Only with materially stronger evidence.  
**Follow-up:** Test the narrower integrated six-level cost-sensitive formulation.

## 2026-08-13 — Raw-context track made primary

**Decision:** Retain normalized scalar state only as a mechanistic control and introduce a raw-context policy projection as the primary validity track.  
**Evidence:** Existing schema directly supplied importance, urgency, interruptibility, action risk, and expected delay cost, which may encode researcher judgment close to the decision target.  
**Alternatives:** Use scalar state as the only benchmark input.  
**Reason:** Avoid evaluating weighted sums over pre-digested label features as if they were general context reasoning.  
**Risk:** Raw-context evaluation adds inference difficulty.  
**Reversible?:** Yes; both tracks are retained.  
**Follow-up:** Freeze track roles before protected evaluation.

## 2026-08-13 — Development v1 replaces pilot for Gate-B validation

**Decision:** Build a diversified 144-scenario development batch with six balanced domains, 24 counterfactual pairs, and six temporal sequences.  
**Evidence:** Executed pre-annotation audit: exact duplicate members 0; structural duplicates 0; unrelated >=0.90 near duplicates 0; metadata leakage findings 0; longest same-domain run 3.  
**Alternatives:** Repair and expand pilot-v0 templates.  
**Reason:** Pilot-v0 structure was fundamentally duplicated and unsuitable for formal ranking.  
**Risk:** Synthetic v1 may still contain lexical shortcuts correlated with future human labels.  
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
