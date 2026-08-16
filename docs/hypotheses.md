# Hypotheses — Protocol v2 preregistration draft

Status: **DRAFT; MUST BE FROZEN BEFORE THE RELEVANT LATER-GATE EVALUATION**

Gate B tests the formal specification itself and therefore does not test candidate-performance hypotheses.

Provisional later-gate hypotheses:

- **H1** A PDA candidate can improve exact specification compliance over preregistered simple baselines without increasing hard-constraint violations.
- **H2** Explicit permission, information-sufficiency, risk, reversibility, and side-effect signals reduce unsafe autonomous `ACT` errors relative to ablated policies.
- **H3** Explicit deferral/timing state improves `IGNORE` versus `WAIT` and timely `NOTIFY` decisions relative to timing-agnostic baselines.
- **H4** Counterfactual and temporal consistency learned on development conditions generalizes to protected/OOD conditions better than simple answer-pattern heuristics.
- **H5** Increased model complexity does not necessarily outperform a transparent deterministic or lightweight hybrid policy on specification-compliance and safety metrics.

These hypotheses have not been tested. No Protocol-v2 baseline ranking, candidate evaluation, or protected-set result is authorized or claimed at Gate B.
