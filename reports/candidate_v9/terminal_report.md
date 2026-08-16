# Candidate-v9 Terminal Report

## Terminal state

`CANDIDATE_V9 DEVELOPMENT FAIL — NO CANDIDATE QUALIFIED`

Candidate-v9 froze V9-B successfully and passed all pre-freeze qualification gates, including zero invalid structured states and zero forbidden/false ACT. The first formal post-freeze holdout, H1 DEV-OOD, failed the preregistered generalization thresholds.

H1 aggregate results: Macro-F1 0.577159 (<0.85), ACT recall 0.236667 (<0.78), ACT precision 1.000, forbidden ACT 0, false ACT 0, state validity 1.000, invalid predicted states 0. Per-action recall: IGNORE 1.000, WAIT 0.493333, SUGGEST 0.503333, NOTIFY 0.536667, ASK 0.550000, ACT 0.236667.

Fail-fast was triggered. H2-H13 were not executed. Protected confirmatory evaluation was not eligible and was not materialized. No Candidate-v9 semantics were changed after freeze or after H1. No H1 individual records were inspected for debugging.

The supported conclusion is narrow: the valid-by-construction state decoder solved the targeted invalid-state failure mode on development and H1 safety validity, but the frozen parser/decoder did not generalize adequately to the preregistered DEV-OOD language distribution.
