# Baseline v0 Plan — Protocol v2 status

Status: **DRAFT — NOT IMPLEMENTED / NOT EVALUATED**

This file preserves early baseline ideas, but no formal baseline is authorized by Protocol-v2 Gate B.

Under the current gate order:

1. Gate B — formal specification validity;
2. Gate C — oracle and benchmark validity;
3. Gate D — baseline integrity.

Therefore formal baseline implementation/ranking must wait until Gate C passes and a separate Gate-D task freezes the actual baseline set against the validated benchmark.

Historical candidate ideas include:

1. majority class;
2. always notify;
3. simple rule systems;
4. decision tree / logistic regression;
5. transparent deterministic or lightweight hybrid policies;
6. optional local/open model policy only if later scientifically justified.

The old urgency/importance weighted-score ideas must not be assumed valid merely because they existed in Protocol v1; Gate D must preregister the actual v2 baselines after Gate C establishes benchmark semantics.

For every eventual formal baseline run, preserve raw predictions, metrics JSON, confusion matrix, run manifest, seed/config/environment, and exact benchmark/spec hashes.

No Protocol-v2 baseline score exists yet. Do not use this draft to claim Gate D progress.
