# Methodology v2 — Specification-Grounded Intervention Control

## Research design

Protocol v2 studies **specification compliance for intervention control**, not general assistant task completion and not human-preference prediction.

The primary validity path is:

```text
explicit structured state
-> frozen versioned specification
-> deterministic reference oracle
-> intervention-control action + trace
-> machine-verifiable evidence
```

Candidate development is forbidden until the current gate sequence authorizes it.

## Structured-state primary track

The formal state is finite and machine validated. Protocol v2 currently represents:

- permission: `not_required | missing | granted`;
- information: `sufficient | insufficient | contradictory`;
- urgency: `none | normal | high | expired`;
- intervention need: `none | optional | material`;
- side-effect scope: `none | local | external`;
- risk: `low | medium | high`;
- reversibility: `reversible | irreversible`;
- deferral availability;
- execution possibility;
- clarification possibility;
- acknowledgement;
- completion.

Invalid cross-field combinations fail closed. The current spec treats external side effects as requiring an explicit permission scope, while a no-side-effect state must use `not_required` permission semantics.

## Action semantics

The six actions are discrete control modes:

- `IGNORE`: no current intervention and no explicit deferred trigger is required.
- `WAIT`: do not intervene now; retain a defined future trigger/observation.
- `SUGGEST`: low-pressure optional recommendation without a material side effect.
- `NOTIFY`: surface material information/change/deadline/risk for awareness.
- `ASK`: request missing information, choice, confirmation, or authorization.
- `ACT`: perform an authorized material action only when required information, permission, risk, reversibility, and execution conditions are satisfied.

No universal scalar ordering is assumed. Legacy Protocol-v1 intensity helpers remain diagnostic/historical only.

## Formal specification and oracle

`spec/proactivity_policy_v2.json` is the transparent machine-readable research policy. It contains the finite schema, invalid-state conditions, hard prohibitions, explicit selection-rule priorities, action semantics, and named invariants.

`src/proactivity/specification/` implements the deterministic reference oracle and validators. The oracle:

- has no network or LLM dependency;
- reads only the formal `state` for its normative decision;
- rejects invalid states;
- derives prohibited actions separately from the selection rules;
- fails closed on an equal-priority action conflict;
- rejects a selected action if it is simultaneously prohibited;
- returns matched-rule, prohibition, eligible-action, spec-version, and spec-hash trace fields.

Scenario IDs, pair IDs, sequence IDs, domain names, file order, annotator fields, and hidden expected-action metadata are not oracle inputs.

## Gate B — Formal Specification Validity

Gate B evaluates the specification itself, not PDA candidate performance.

Required checks include:

1. exact schema validity and invalid-combination rejection;
2. exhaustive bounded-state enumeration;
3. deterministic repeated oracle output;
4. equal-priority conflict detection and precedence-cycle checking;
5. zero valid-state fallthrough;
6. rule reachability diagnostics;
7. complete decision traces;
8. ACT permission/information/risk/reversibility/execution invariants;
9. completed-state non-intervention invariant;
10. counterfactual permission/risk/information degradation tests;
11. explicit temporal transition tests without assuming monotonic escalation;
12. metadata/domain/row-order independence;
13. CI across Python 3.10, 3.11, and 3.12.

Hard specification and safety invariants use fail-closed / zero-tolerance criteria at Gate B.

## Protocol-v2 development generator

`scripts/generate_development_v2.py` deterministically samples explicit valid states and adds canonical reachability states so all six action modes are exercised. Each `oracle_action` and selected rule is recomputed by the frozen oracle. A separate handwritten gold-label table does not exist.

The v2 development artifact is Gate-B transport/reachability infrastructure only. Formal benchmark validity belongs to Gate C.

## Counterfactual and temporal methodology

Counterfactual expectations are derived from the frozen specification before candidate evaluation. Current Gate-B checks start from oracle-eligible ACT states and verify that removing required permission, increasing risk, or degrading information disables autonomous action.

Temporal checks are explicit predicate/rule checks rather than a global scalar escalation assumption. The reference Gate-B sequence exercises defer, urgent notification, acknowledgement/defer, and completion/silence behavior.

## Raw-context secondary track

Protocol v1 made raw-context input the primary validity path. Protocol v2 changes this: natural-language context is secondary and may later test state extraction, paraphrase robustness, or adversarial rendering.

If text is deterministically rendered from a structured state, the generator-known state remains the source of truth. The reference oracle must not infer normative labels from prose.

## Dataset migration

The 144 `development_v1` scenarios are preserved but are not assigned Protocol-v2 gold decisions by after-the-fact prose interpretation. The migration audit records all 144 as ambiguous with respect to the complete new semantic state. Their design concepts and infrastructure remain reusable.

## Historical human-validation track

Protocol-v1 annotation packets, completed-return validation, immutable archive tooling, agreement/kappa analysis, and negative evidence are preserved. A future human study may test external validity or preference alignment, but it is optional and does not block the primary Protocol-v2 gate sequence.

## Evaluation principle

Oracle correctness means correctness **with respect to the frozen research specification**. It does not imply that the specification is universally desirable or human-preferred. Later candidate metrics must keep this claim boundary explicit and use denominators defined in `docs/metric_definitions.md`.

## Gate order

Gate A: scope / claim boundary / prior art.  
Gate B: formal specification validity.  
Gate C: oracle and benchmark validity.  
Gate D: baseline integrity.  
Gate E: candidate evidence.  
Gate F: protected/OOD validation.  
Gate G: robustness/adversarial/invariant stress testing.  
Gate H: ablation/reproducibility/independent reproduction/final claim audit.

This migration mission stops before Gate C even if Gate B passes.
