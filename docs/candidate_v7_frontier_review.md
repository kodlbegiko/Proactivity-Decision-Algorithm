# Candidate-v7 Frontier Review

## Research framing
Candidate-v6 demonstrated that near-perfect average factor accuracy can still permit forbidden ACT under distribution shift. Candidate-v7 therefore treats ACT as a conjunctive, high-consequence decision rather than an ordinary classification label.

## Relevant methodological directions
1. **NLI-style three-way semantics**: represent entailment, contradiction, and unknown rather than binary truth.
2. **Selective prediction**: abstain at the factor-certainty layer when evidence is insufficient; do not hard-code the final action.
3. **Conformal/calibration-inspired uncertainty controls**: use uncertainty as a veto signal, while separately measuring action coverage to prevent safety-by-collapse.
4. **Neurosymbolic proposition structure**: decompose propositions and reason over explicit factor evidence instead of mapping text directly to action.
5. **Metamorphic/counterfactual testing**: mutate one ACT-critical prerequisite and require ACT to disappear.

## Candidate-v7 design consequence
The implemented lineage uses proposition/clause decomposition, factor-specific concept evidence, contradiction and supersession handling, OOD/ambiguity scoring, conservative state projection, and an explicit ACT eligibility gate. No direct six-action classifier is used for Candidate-v7.

## Scope boundary
The benchmark remains synthetic and controlled. Passing it would support only benchmark-bounded semantic-state generalization, not unrestricted natural-language understanding or production safety.
