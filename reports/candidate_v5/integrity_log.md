# Candidate-v5 Research Integrity Log

Status: TERMINAL — FAIL CLOSED

## 2026-08-15 — lineage start

- Branch `research/candidate-v5-generalization-recovery` was created directly from Candidate-v4 terminal commit `370aac305c14c4ddc2fa2f782cbb3f0fdde4f630`.
- No Candidate-v5 development data, candidate implementation, model selection result, or Candidate-v5 protected dataset existed at branch creation.
- Candidate-v4 aggregate terminal was verified from `gate_recovery_v4/fresh_confirmatory_terminal.json` without reading its individual protected payloads.

## Integrity incident IR-V5-001

During historical-lineage audit, the GitHub connector action `fetch_commit` was invoked on Candidate-v3 terminal commit `2a9e2f0841ef145a5b27ddd2ed8a866dba7ec4f4` to verify the terminal record.

The connector unexpectedly returned a commit diff that contained individual Candidate-v3 confirmatory rows in addition to aggregate/administrative material. This exceeded the intended read scope and violated the Candidate-v5 mission's hard quarantine rule prohibiting access to historical Candidate-v3/Candidate-v4 protected individual examples.

### Containment

- The returned individual rows are not copied into this repository, reports, benchmark generators, candidate code, or any Candidate-v5 artifact.
- Candidate-v5 development was stopped before any development corpus was generated.
- No Candidate-v5 architecture was implemented or selected after the incident.
- No Candidate-v5 source freeze occurred.
- No Candidate-v5 protected seed or protected dataset was generated.
- No Candidate-v5 protected evaluation was run.
- No attempt is made to claim that the contaminated execution context can prove independence from historical protected evidence.

### Integrity decision

Fail closed. The current Candidate-v5 execution lineage is invalid for scientific development/confirmatory claims. The branch is preserved as negative integrity evidence and must not be reused as the basis for a qualified Candidate-v5.

Terminal state for this mission:

`FRESH CONFIRMATORY INVALID — EVALUATION INTEGRITY FAILURE`
