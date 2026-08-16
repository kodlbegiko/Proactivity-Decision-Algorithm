# Candidate-v6 Development Terminal Report

**Terminal State:** `CANDIDATE V6 DEVELOPMENT FAIL — NEW ARCHITECTURE REQUIRED`

## Identity

- Branch: `research/candidate-v6-structured-latent-reasoning`
- Base Commit: `a4e73fb0f16694efbe75ace8c088075fe83c9303`
- Preregistration Commit: `a077a6bf5e522e85c84820efbe3c9ae350d126bc`
- Candidate Source Commit: `1ce0d267138d07805ddc3337f871e6fddc24e9f9`
- Dataset Freeze Commit: `ea705a8875415f29ecb82cb6d60ada5b353ff484`
- Selection Commit: `064d78aab4d93b64e19cc1793b53ed0c4932decc`
- Qualification Commit: `f69c87478dbaca25be670977c077904d17831791`
- Terminal Evidence Commit: `4b58307b086a1d42396abfb1329680f2222d3d77`
- CI Run ID: `31921106848`
- Model: `sentence-transformers/all-MiniLM-L6-v2@1110a243fdf4706b3f48f1d95db1a4f5529b4d41`

## Research Integrity

- Candidate-v3 protected access: `0`
- Candidate-v4 protected access: `0`
- Candidate-v5 holdout reuse: `False`
- Protected leakage: `NONE_DETECTED`
- Chronology: `PASS`

## Validation

- Accuracy: `0.812222`
- Macro-F1: `0.819593`
- Exact latent-state reconstruction: `0.292222`
- Mean factor accuracy: `0.922407`
- ACT-critical factor accuracy: `0.943175`
- Critical UNKNOWN rate: `0.056825`
- Forbidden ACT: `0`
- Invalid action: `0`

## Holdout Summary

- Development OOD macro-F1: `0.915749`
- Lexical macro-F1: `0.381556`
- Rendering macro-F1: `0.610590`
- Compositional macro-F1: `0.877618`
- Negation macro-F1: `0.166098`
- Counterfactual exact-pair: `0.855556`
- Invariance action consistency: `0.844444`

## Architecture Evidence

- Selected architecture: `V6A`
- Selected config: `V6A-06`
- V6A, V6B, V6C family summaries, baselines, and ablations are preserved in `gate_recovery_v6/terminal.json`.

## Scientific Interpretation

The structured latent-state direction did not satisfy every preregistered mandatory criterion. Failed criteria: invariance, latent_state_recovery, lexical, negation, no_catastrophic_collapse, rendering, safety, validation. The lineage is therefore frozen as a development FAIL without holdout tuning or rescue. The preserved factor, calibration, counterfactual, invariance, baseline, and ablation evidence should be used only as aggregate architectural evidence for a future fresh lineage.

## Final Authorization

Candidate-v6 Fresh Independent Protected Confirmatory: **NOT AUTHORIZED**

Gate G: **NOT EXECUTED**
