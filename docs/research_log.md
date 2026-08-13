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
**Reason:** This is an infrastructure-specific transport failure and does not prevent repository inspection, branch control, commits, or evidence preservation through the connector.  
**Risk:** Local git command provenance is unavailable for initialization.  
**Reversible?:** Yes; another environment can later clone and independently audit the remote commits.  
**Follow-up:** Preserve exact remote commit SHAs and local test outputs.

## 2026-08-13 — Research gap narrowed

**Decision:** Reject the broad claim that proactive-agent benchmarks are absent. Test a narrower intervention-control contribution with explicit silence/deferral, permission, risk, and asymmetric costs.  
**Evidence:** ProactiveEval, ProActor, π-Bench, Pare-Bench, ProAgentBench and NIABench materially overlap with proactive evaluation/timing.  
**Alternatives:** Continue with a generic “proactive assistant benchmark.”  
**Reason:** That would be poorly differentiated and scientifically misleading.  
**Risk:** A deeper review may find an equivalent formulation and remove novelty.  
**Reversible?:** Yes; a negative novelty result is acceptable.  
**Follow-up:** Complete systematic comparison before publication claims.

## 2026-08-13 — Stop before candidate development

**Decision:** Build benchmark/annotation infrastructure but do not tune a substantive candidate yet.  
**Evidence:** No independent annotation agreement has been measured.  
**Alternatives:** Generate labels from one researcher and immediately optimize candidate performance.  
**Reason:** That would risk measuring researcher self-consistency rather than proactive decision quality.  
**Risk:** Slower visible progress, stronger evidence quality.  
**Reversible?:** Candidate work begins once Gate B passes.  
**Follow-up:** Obtain independent labels for the pilot batch and compute agreement.

## 2026-08-13 — Local validation incident

**Decision:** Treat the first dataset validation failure as a real failed check, fix the malformed timestamp, then rerun all checks.  
**Evidence:** Initial validator rejected `2026-08-15T010:00:00Z`; after correction, dataset validation reported 24 valid unique scenarios and pytest reported 9 passed.  
**Alternatives:** Ignore the validator failure because unit tests passed.  
**Reason:** Dataset validity is independent evidence and must not be hidden.  
**Risk:** Pilot generator needs stronger timestamp regression coverage.  
**Reversible?:** Yes.  
**Follow-up:** Add CI validation of the pilot JSONL.
