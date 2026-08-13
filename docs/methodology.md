# Methodology v0

## Research design

Stage 1 is a controlled, model-agnostic benchmark study of proactive intervention decisions. Candidate development is forbidden until benchmark validity is supported.

## Scenario representation

Each scenario stores context only. Ground-truth annotations live separately to reduce accidental label leakage.

Core fields include domain; user activity/workload/interruptibility; event importance/urgency/deadline/confidence/evidence reliability; task acknowledgement/completion; action risk/reversibility; expected delay cost; permission state; context freshness; and history.

## Benchmark strategy

1. Create synthetic-but-realistic development scenarios for taxonomy/pipeline testing.
2. Audit lexical/template/metadata leakage.
3. Run independent human annotation.
4. Compute raw agreement and Cohen/Fleiss kappa as appropriate.
5. Revise taxonomy/guidelines only on development material.
6. Freeze benchmark schema and evaluation rules.
7. Create protected set with a separate generation/annotation batch.
8. Hash and freeze protected artifacts before formal candidate evaluation.

## Ground truth

Preferred action may be accompanied by an acceptable-action set where legitimate ambiguity exists. Formal handling of acceptable sets must be frozen before protected evaluation.

## Gates

### Gate A — Problem Definition
Requires explicit RQs, scope, operational taxonomy, and evidence-backed gap.

### Gate B — Benchmark Validity
Requires frozen schema, documented labels, leakage audit, and acceptable independent annotation agreement.

No formal baseline leaderboard or candidate optimization is allowed before Gate B.

## Planned metrics after Gate B

- accuracy / macro F1 / per-class precision-recall
- confusion matrix
- intervention precision
- critical-event recall
- false interruption rate
- missed critical-event rate
- premature intervention rate
- unsafe autonomy rate
- over/under-escalation
- preregistered cost-sensitive utility profiles

## Protected-evaluation rule

Exactly one confirmatory protected run per frozen candidate, except an infrastructure failure that prevents a valid evaluation. Performance failure is not infrastructure failure.
