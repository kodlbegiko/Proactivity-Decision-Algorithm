# Candidate-v12 Integrity Boundaries

Forbidden and not inspected: V11Q raw protected examples/labels, per-example protected predictions/errors, protected counterfactual/invariance realizations, and hidden protected generator content. Candidate-v11 source was not modified.

The development CI verifies the frozen V11 source blob, checks no diff to V11Q/benchmark/protected-artifact paths, and scans V12 source for protected module/test references. Hash-only identity checks do not expose protected sentence-level content.

Allowed inputs: public PDA-SPEC-v2, frozen repository code, declassified V11Q aggregates, and fresh Candidate-v12 synthetic development data. Integrity status: PASS.