# Candidate-v5 Historical Lineage Audit

## Scope

This audit was initiated before Candidate-v5 development, as required by the mission. The intended boundary was administrative/aggregate historical verification only.

## Verified repository state

- Repository: `kodlbegiko/Proactivity-Decision-Algorithm`
- Candidate-v5 mission branch: `research/candidate-v5-generalization-recovery`
- Branch base: Candidate-v4 terminal commit `370aac305c14c4ddc2fa2f782cbb3f0fdde4f630`
- Candidate-v4 terminal artifact: `gate_recovery_v4/fresh_confirmatory_terminal.json`
- Candidate-v4 terminal state: `FRESH CONFIRMATORY FAIL — CANDIDATE V4 LINEAGE TERMINATED`
- Candidate-v4 aggregate terminal reports zero forbidden ACT and zero invalid actions, while main accuracy, macro-F1, class-recall coverage, lexical stress, compositional stress, counterfactual exact-pair, and invariance criteria failed.
- Candidate-v3 confirmatory branch exists at `research/proactivity-candidate-v3-confirmatory`; its head commit message records Candidate-v3 fresh confirmatory terminal evidence.
- A separate pre-existing branch `research/candidate-v5-semantic-generalization` exists. It is not used by this mission because its preregistered criteria differ from the uploaded Candidate-v5 mission. It remains a distinct lineage and is not overwritten.

## Intended quarantine

Historical protected example payloads were prohibited from Candidate-v5 development, including Candidate-v3 and Candidate-v4 confirmatory datasets, labels, predictions, parser diagnostics, per-example errors, counterfactual pairs, lexical stress examples, and compositional examples.

Administrative artifacts, protocols, preregistrations, public specification/source, aggregate terminal facts, and non-protected development documentation were intended to remain readable.

## Integrity failure

Audit action `fetch_commit` on Candidate-v3 terminal commit `2a9e2f0841ef145a5b27ddd2ed8a866dba7ec4f4` returned a commit diff containing individual Candidate-v3 confirmatory rows. The access was not intended, but the hard boundary is access-based, not intent-based.

This makes the current execution context contaminated for Candidate-v5 scientific development. Because the mission explicitly forbids reading historical protected individual examples, the lineage cannot honestly claim protected independence.

## Disposition

- Candidate-v5 development: NOT STARTED
- Candidate-v5 architecture search: NOT STARTED
- Candidate-v5 development datasets: NOT GENERATED
- Candidate-v5 freeze: NOT CREATED
- Candidate-v5 protected seed: NOT GENERATED
- Candidate-v5 protected evaluation: NOT EXECUTED
- Research-integrity status: FAIL

Terminal state:

`FRESH CONFIRMATORY INVALID — EVALUATION INTEGRITY FAILURE`
