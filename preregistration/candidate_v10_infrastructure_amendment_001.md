# Candidate-v10 Infrastructure Amendment 001

Status: **FROZEN BEFORE ANY Candidate-v10 QUALIFICATION METRIC WAS PRODUCED**

## Incident

The first authorized development-qualification workflow reached estimator construction but failed during `fit()` before any Candidate-v10 architecture metric was computed or written. `scikit-learn==1.8.0` rejects multiclass `LogisticRegression(solver='liblinear')` unless an explicit one-vs-rest wrapper is used.

## Classification

This is classified as a dependency/runtime compatibility incident, not a semantic evaluation result.

Evidence boundary at the incident:

- integrity precheck: PASS
- mandatory unit tests: 27/27 PASS
- fresh dataset materialization began
- model fitting did not complete
- architecture predictions: none
- qualification metrics: none
- architecture selection: none
- formal H1-H15: not materialized
- protected evaluation: not materialized

## Amendment

To preserve the already-preregistered Candidate semantics and training procedure without changing architecture code, solver, features, random state, seeds, data generator, splits, thresholds, decoder, policy, uncertainty behavior, or selection rule, the runtime pin is changed only from:

`scikit-learn==1.8.0`

to:

`scikit-learn==1.7.2`

In scikit-learn 1.7.x, the registered `liblinear` multiclass one-vs-rest behavior remains available; version 1.8 removes that implicit behavior. No Candidate-v10 benchmark result existed when this amendment was frozen.

## Integrity declaration

- Candidate semantics changed: false
- architecture changed: false
- features changed: false
- classifier family changed: false
- solver changed: false
- hyperparameters changed: false
- seeds changed: false
- data changed: false
- split inventories changed: false
- thresholds changed: false
- result-driven tuning performed: false
- Candidate-v9 H1 individual evidence accessed: false

The next workflow attempt is an infrastructure retry of the same preregistered semantic qualification, not a semantic rerun after observing performance.
