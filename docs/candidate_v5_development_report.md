# Candidate-v5 Fresh-Lineage Development Terminal Report

**Terminal state:** `CANDIDATE V5 DEVELOPMENT FAIL — NEW ARCHITECTURE REQUIRED`

## Integrity
- Base: `370aac305c14c4ddc2fa2f782cbb3f0fdde4f630`
- Preregistration: `d064d8cf66e2354d38e0b0b69ba5bffd6ff386ef`
- Candidate-v3 protected access: 0
- Candidate-v4 protected access: 0
- Candidate-v4 development corpus reused: no

## Selected
- Architecture: `V5C`
- Config: `{"ambiguity_margin": 0.03, "architecture": "V5C", "hypothesis_weight": 0.25, "similarity_floor": 0.35}`
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Model revision: `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`

## Metrics
- development_ood: macro-F1 `0.097780`, accuracy `0.131667`
- lexical_holdout: macro-F1 `0.168668`, accuracy `0.244444`
- rendering_holdout: macro-F1 `0.112081`, accuracy `0.163889`
- compositional_holdout: macro-F1 `0.137058`, accuracy `0.219444`
- Counterfactual exact-pair: `0.023438`
- Invariance consistency: `0.433333`
- ACT-critical accuracy: `0.412245`
- Critical unknown rate: `0.294218`

## Criteria
- validation: `FAIL`
- development_ood: `FAIL`
- lexical_holdout: `FAIL`
- rendering_holdout: `FAIL`
- compositional_holdout: `FAIL`
- counterfactual: `FAIL`
- invariance: `FAIL`
- latent_recovery: `FAIL`
- safety: `PASS`
- no_catastrophic_collapse: `PASS`
- invalid_action_zero: `PASS`

## Claim boundary
This is development qualification only under Protocol-v2. It is not protected-confirmatory PASS, Gate G PASS, Gate H PASS, production readiness, or universal language understanding.
