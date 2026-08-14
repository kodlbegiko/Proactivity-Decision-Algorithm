# Protected Validation Protocol — Protocol v2 draft

Status: **DRAFT — NO PROTECTED SET EXISTS / GATE F NOT AUTHORIZED**

This document specifies future protected evaluation hygiene only. It does not create a protected set or claim Gate-F progress.

## Freeze package

Before protected evaluation:

- frozen candidate commit SHA;
- candidate code hash;
- frozen protected dataset SHA-256;
- frozen specification/oracle version and SHA;
- config and seed;
- exact metric versions;
- hypotheses and acceptance thresholds;
- statistical test where applicable;
- stopping rule.

## Protocol-v2 source of expected decisions

For the primary specification-grounded track, protected expected decisions must derive from generator-known formal state + the already frozen applicable specification/oracle contract. They must not require human annotation and must not be separately handwritten after candidate behavior is observed.

A separate optional human-preference study, if ever executed, is external-validity evidence and is not part of this primary protected-validation protocol.

## Execution rule

One confirmatory protected execution per frozen candidate. A retry is allowed only if infrastructure failure prevented a valid evaluation from occurring.

Algorithm performance failure is not infrastructure failure.

## Contamination rule

If protected states, expected decisions, outputs, or derived metrics influence candidate tuning, rule changes, candidate selection, or benchmark edits, mark:

`PROTECTED SET CONTAMINATED`

and construct a new independently generated protected set under the already frozen generation/specification rules. Do not repair a protected set in response to candidate failure.
