# Candidate-v5 Terminal Report

## Terminal State

`FRESH CONFIRMATORY INVALID — EVALUATION INTEGRITY FAILURE`

## Why the mission terminated

The Candidate-v5 mission explicitly prohibits reading individual Candidate-v3/Candidate-v4 protected confirmatory examples. During the mandatory historical-lineage audit, a GitHub commit-level fetch used to verify Candidate-v3 terminal evidence returned individual Candidate-v3 confirmatory rows in the connector response.

The read was unintended and no Candidate-v5 development work had begun, but the scientific boundary is violated once the execution context has been exposed. Continuing architecture design, benchmark generation, model selection, source freeze, or fresh confirmatory evaluation from the same context would make an independence claim unverifiable.

The mission therefore fails closed rather than treating intent as sufficient evidence of non-contamination.

## Candidate

- selected architecture: NONE
- version: Candidate-v5 lineage invalid before development
- freeze SHA: NONE
- source SHA-256: NONE

## Development

Not executed after the integrity incident.

- validation metrics: NOT AVAILABLE
- dev-OOD metrics: NOT AVAILABLE
- lexical: NOT AVAILABLE
- compositional: NOT AVAILABLE
- counterfactual: NOT AVAILABLE
- invariance: NOT AVAILABLE
- uncertainty: NOT AVAILABLE

## Protected

Not executed.

- seed: NOT GENERATED
- dataset hash: NOT GENERATED
- candidate metrics: NOT AVAILABLE
- baseline metrics: NOT AVAILABLE
- bootstrap CI: NOT AVAILABLE
- safety metrics: NOT AVAILABLE
- stress-set metrics: NOT AVAILABLE

## Integrity

- historical protected accessed during this execution: YES — unintended connector overfetch
- historical protected used for development: NO
- Candidate-v5 protected generated after freeze: NOT APPLICABLE
- candidate modified after freeze: NOT APPLICABLE
- rerun: NO
- leakage status: EXECUTION_CONTEXT_CONTAMINATED_BY_UNINTENDED_HISTORICAL_PROTECTED_OVERFETCH
- invalidated runs: current Candidate-v5 execution lineage

## GitHub

- repository: `kodlbegiko/Proactivity-Decision-Algorithm`
- branch: `research/candidate-v5-generalization-recovery`
- base commit: `370aac305c14c4ddc2fa2f782cbb3f0fdde4f630`
- integrity incident: `IR-V5-001`

## Claim Boundary

### Supported

- Candidate-v4 is historically terminated by fresh confirmatory FAIL according to its aggregate terminal artifact.
- The new Candidate-v5 branch was created from the Candidate-v4 terminal commit.
- This execution detected and preserved a research-integrity incident before Candidate-v5 development.
- No Candidate-v5 development corpus, candidate implementation, candidate freeze, protected seed, protected dataset, or protected score was produced after the incident.

### Not Supported

- Candidate-v5 development qualification
- Candidate-v5 natural-language generalization
- Candidate-v5 protected confirmatory performance
- Gate G authorization
- Gate H authorization
- closed-loop readiness

### Known Failures

- Historical protected quarantine was breached by an unintended commit-diff overfetch during administrative verification.

### Remaining Critical Path

A scientifically independent retry requires a fresh execution context that does not contain the exposed historical protected rows and that verifies historical state using allow-listed aggregate files/branch metadata only. The invalid branch must remain preserved as negative integrity evidence and must not be converted into a qualified Candidate-v5 lineage.
