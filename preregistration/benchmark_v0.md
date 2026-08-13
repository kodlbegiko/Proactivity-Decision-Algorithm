# Benchmark v0 Preregistration Draft

Status: **DRAFT — NOT FROZEN**

## Unit of evaluation

A scenario-level proactive decision from standardized context to one of six actions.

## Planned domains

- calendar/deadlines
- study/coursework
- work/projects
- communication
- travel/logistics
- device/digital state
- file/document workflow
- shopping/logistics

## Required scenario families

Critical intervention; useful non-critical; premature intervention; redundant intervention; distracting intervention; ambiguous context; unsafe autonomy; false urgency; delayed benefit; conflicting signals.

## Split policy

- development: visible; used for taxonomy and pipeline iteration
- validation: visible labels; used only after taxonomy stabilization
- protected_test: labels hidden from candidate development; separately generated/annotated and frozen
- optional adversarial and cross-domain sets

## Protected-set requirements

Before any formal candidate run, record SHA-256, scenario count, generation method, raw/adjudicated label artifacts, freeze commit, and metric implementation version/hash.

## Leakage audit requirements

- keyword/label correlation
- template-ID shortcuts
- scenario ordering
- metadata/filename leakage
- duplicated structures
- shuffled-feature control

## Gate condition

This benchmark cannot be frozen until independent annotation agreement meets the preregistered thresholds or the protocol is revised and re-piloted.
