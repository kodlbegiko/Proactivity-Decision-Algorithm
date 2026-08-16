# Candidate-v9 Normative State-Space Audit

The PDA-SPEC-v2 schema has 62,208 theoretical structured-state combinations. Exactly 20,736 violate the two normative permission-scope constraints, leaving 41,472 valid states.

Invalid reasons:

- `I_EXTERNAL_NEEDS_PERMISSION_SCOPE`: 6,912
- `I_NO_SIDE_EFFECT_HAS_NO_PERMISSION_SCOPE`: 13,824

Oracle action distribution over all 41,472 valid states:

- IGNORE: 24,192
- WAIT: 7,518
- ASK: 5,688
- SUGGEST: 2,076
- NOTIFY: 1,938
- ACT: 60

The valid-state-space canonical SHA-256 is `5e7af8d313ab2fa846c9ebb3d1c72151aebbb99dc30b077611ed7ed229bc948f`.

Candidate-v9 decoders are required to construct outputs only inside this valid subset; invalid combinations may not reach the normative policy.
