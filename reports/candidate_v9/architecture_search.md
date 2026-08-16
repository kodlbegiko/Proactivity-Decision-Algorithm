# Candidate-v9 Architecture Search

Selected: **V9-B**.

V9-A is a post-hoc projection baseline and is structurally ineligible for final selection despite benchmark performance. V9-B and V9-C both satisfy the preregistered qualification gates. They tie on state validity, forbidden/false ACT, counterfactual ACT-disable, ACT precision/recall, exact state accuracy and Macro-F1; the preregistered final tie-break is lower complexity, selecting V9-B.

V9-B performs joint decoding over normative-valid permission/side-effect pairs. V9-C preserves contradiction as unresolved evidence before the same constrained valid-state search and remains the stronger uncertainty-oriented architecture, but the preregistered selection rule does not permit preferring it after a complete metric tie.
