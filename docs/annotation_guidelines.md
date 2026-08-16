# Annotation Guidelines v0

Status: **PILOT ONLY — NOT FROZEN**

Annotators must work independently and must not see policy predictions or other annotators' labels before submitting first-pass labels.

## Required decision sequence

1. Does the situation warrant any intervention at all?
2. If yes, is **now** the right time?
3. What is the expected benefit of intervening now?
4. What is the interruption cost now?
5. Is critical information missing or contradictory?
6. Is explicit user permission required before taking action?
7. Which intervention class best matches the above?

## Action labels

- **IGNORE** — no current or future intervention needed for this event.
- **WAIT** — do not interrupt now; retain for later reevaluation.
- **SUGGEST** — low-intensity optional recommendation.
- **NOTIFY** — salient information should be surfaced now.
- **ASK** — clarification/permission is required.
- **ACT** — action is authorized, sufficiently certain, low enough risk, and appropriately timed.

## Fail-closed rules

Prefer `ASK` or `WAIT` over `ACT` when permission is unclear, action is high-consequence/poorly reversible, confidence or evidence reliability is inadequate, context is stale, or evidence conflicts.

## Ambiguity

Annotators record:

- `preferred_action`
- `acceptable_actions` (pipe-separated set, e.g. `WAIT|SUGGEST`)
- annotation confidence (1–5)
- optional rationale

Acceptable-action sets are only for cases where multiple actions are genuinely defensible under the frozen semantics.

## Agreement gate

Before benchmark freeze, target:

- raw agreement on preferred action >= 0.80
- Cohen's kappa (2 labelers) or appropriate multi-rater kappa >= 0.60

If either gate fails, do not tune a candidate. Diagnose taxonomy ambiguity, guideline insufficiency, or inherently subjective cases first.

## Adjudication

1. Preserve original independent labels.
2. Compute agreement before discussion.
3. Discuss disagreements only after first-pass metrics are archived.
4. Store adjudicated labels separately from raw labels.
