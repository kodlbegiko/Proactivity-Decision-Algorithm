# Candidate-v12 Qualification Integrity Incident

## Decision

`QUALIFICATION INVALID — FROZEN CANDIDATE IDENTITY MISMATCH`

Canonical terminal state:

`CANDIDATE_V12 QUALIFICATION INVALID — EVALUATION_INTEGRITY_FAILURE`

## What failed

The preregistered/freeze-manifest values described as frozen blob identities do not resolve as Git blob objects in `kodlbegiko/Proactivity-Decision-Algorithm`, while the files at frozen commit `7fe5c915c8139888bc4925282d11b42a223cbf25` resolve to different Git blob SHAs.

| Path | Declared frozen identity | Actual Git blob at frozen commit |
|---|---|---|
| `src/proactivity/candidate_v12.py` | `64810128af5e07946972c0c2de75c6988931c8e3` | `64894713bfd37a7ef4638c07a397c855879e365d` |
| `src/proactivity/candidate_v12_frames.py` | `6243698ac62b74066696de7a6ff65e924ef44cbd` | `624eb183884e4d6260a3b6572ba15bf950f5b04d` |
| `src/proactivity/candidate_v12_final_v2.py` | `75252352388e326a71c7ddbb7002b4bab45ca98c` | `75277226911ea281bf7eee7542bf666feddea300` |
| `src/proactivity/specification/schema.py` | `28d7ab86922a4b40e030f2f21f42359d68beed30` | `28d7aed6bbdcfb0dce79b8cd0c2db9d96cd32c82` |
| `spec/proactivity_policy_v2.json` | `e343554b0d003b90d2179466654ffc3c6858e54a` | `e34345bf76179d2c989d9da2effaa013792925fe` |

Direct Git blob lookup of every declared identity returned HTTP 404 / Not Found. The freeze manifest repeats the declared values but does not define a separate content-hash algorithm that would make them independently reproducible. Therefore the declared values cannot serve as verifiable Git blob identities.

## Controls that passed

- Frozen commit exists: `7fe5c915c8139888bc4925282d11b42a223cbf25`.
- Validated source commit exists: `e8ed2afa0171734450b4d56e04420b4cb1007423`.
- The validated source commit tree is `08dd7917740c3343680311cbf319e464b2034168`.
- The freeze commit is one commit ahead of the validated source commit.
- The freeze commit changes reports/docs/artifacts only; the Candidate-v12 source, schema and policy paths are not changed by that freeze commit.
- Qualification preregistration was committed before any protected example generation.

These controls do not cure the declared identity mismatch.

## Protected-data status

No protected qualification examples were generated. No qualification seed was exposed. No Candidate-v12 protected evaluation was executed. No performance metrics were observed. The preregistered seed commitment therefore never produced a protected dataset.

## Integrity consequence

The protocol requires an immediate INVALID stop on any frozen identity mismatch. Continuing to 6,000 examples would create scientifically uninterpretable results because the identity predicate being qualified is not reproducible from the declared blob IDs.

## Authorized repair

Do not modify Candidate-v12. Repair only the identity infrastructure in a new qualification lineage:

1. Define exactly one reproducible identity scheme (prefer Git blob SHA for repository files).
2. Regenerate/fix the freeze identity manifest from the frozen commit without changing Candidate-v12 source.
3. Independently verify every identity against Git.
4. Start a fresh qualification branch/preregistration and use a fresh seed commitment.
5. Only then generate protected examples.
