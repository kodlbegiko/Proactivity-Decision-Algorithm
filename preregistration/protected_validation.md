# Protected Validation Protocol

Status: **DRAFT — NO PROTECTED SET EXISTS**

## Freeze package

Before protected evaluation:

- frozen candidate commit SHA
- candidate code hash
- protected dataset SHA-256
- config and seed
- exact metric versions
- hypotheses and acceptance thresholds
- statistical test
- stopping rule

## Execution rule

One confirmatory protected execution per frozen candidate. A retry is allowed only if infrastructure failure prevented a valid evaluation from occurring.

Algorithm performance failure is not infrastructure failure.

## Contamination rule

If protected labels influence tuning, rule changes, candidate selection, or benchmark edits, mark:

`PROTECTED SET CONTAMINATED`

and construct a new independently generated/annotated protected set.
