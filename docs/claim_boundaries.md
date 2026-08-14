# Protocol v2 Claim Boundaries

## Supported claim categories, conditional on later gate evidence

Protocol v2 may evaluate and eventually support narrowly scoped claims about:

- compliance with the repository's frozen proactivity specification;
- deterministic mapping from explicit structured state to intervention-control mode;
- permission-sensitive autonomous action constraints;
- information/risk/reversibility/side-effect constraints;
- counterfactual policy consistency;
- temporal-rule consistency;
- invariant satisfaction and fail-closed invalid-state handling;
- rule/prohibition traceability;
- reproducibility of machine-grounded benchmark generation and evaluation;
- robustness or OOD behavior only after the corresponding later gates execute.

## Claims explicitly out of scope

Without a separate human study, Protocol v2 must not claim:

- human preference alignment;
- that the oracle represents what users generally want;
- universal or objective correctness of the six intervention modes;
- user satisfaction, trust, comfort, or psychological validity;
- social acceptability;
- ecological validity beyond supported modeled/synthetic conditions;
- general personal-assistant quality;
- human consensus or annotation reliability.

## Interpretation of the oracle

The deterministic oracle is the executable reference implementation of a **research policy**. Agreement with it means specification compliance. It does not constitute evidence that the policy is universally desirable.

## Action taxonomy caveat

`IGNORE`, `WAIT`, `SUGGEST`, `NOTIFY`, `ASK`, and `ACT` are discrete intervention-control modes. A single universal scalar ordering is not part of the formal claim. Existing v1 intensity helpers remain historical/diagnostic only.

## Human validation

Protocol-v1 annotation infrastructure remains available for optional future external-validity or preference studies. Such evidence, if ever collected, must be reported separately rather than retroactively treated as part of Protocol-v2 Gate B.
