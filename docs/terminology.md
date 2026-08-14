# Terminology

## Decision classes

### IGNORE
No intervention is warranted now and the event does not need to be retained for a later intervention decision.

### WAIT
Do not intervene now, but retain the event because a later time or additional evidence may change the decision.

### SUGGEST
Offer a low-intensity optional recommendation. The user can ignore it without immediate consequence.

### NOTIFY
Deliver salient information because delayed awareness has meaningful expected cost, but no authorization is required merely to inform.

### ASK
Request clarification, missing information, or permission because safe continuation is not justified from current evidence.

### ACT
Execute an action only within pre-existing authorization, with adequate confidence and acceptable risk/reversibility.

## Required distinctions

- `IGNORE != WAIT`: retention and future reevaluation differ.
- `SUGGEST != NOTIFY`: urgency/salience differ.
- `ASK != ACT`: authorization and uncertainty differ.

## Binary intervention grouping

For secondary binary metrics only:

- non-intervention: `IGNORE`, `WAIT`
- intervention: `SUGGEST`, `NOTIFY`, `ASK`, `ACT`

This grouping does not collapse the six-class taxonomy.

## Safety semantics

`ACT` is fail-closed. Missing permission, high risk, contradictory evidence, or insufficient confidence must not default to autonomous action.
