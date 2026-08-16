# Threats to Validity

## Construct validity

- “Useful intervention” is subjective and may not map cleanly to one label.
- Six action classes may be too granular or may omit modality dimensions.
- Scalar fields such as urgency and benefit may encode annotator assumptions rather than observable state.

## Internal validity

- Synthetic scenario templates can leak labels.
- Utility weights can be tuned post hoc to favor a candidate.
- A single researcher can unintentionally encode the intended policy into labels.
- Repeated protected runs would convert confirmation data into development data.

## External validity

- Synthetic contexts may not reproduce real user timing, workload, or history patterns.
- Study/work/travel domains may not transfer to high-stakes autonomy.
- Offline snapshots may overestimate longitudinal performance.

## Statistical conclusion validity

- Small per-class counts can make macro metrics unstable.
- Class imbalance can inflate accuracy.
- Kappa can be sensitive to prevalence.
- Multiple candidate iterations increase false-discovery risk if not preregistered.

## Novelty risk

2026 literature already contains several proactive-agent benchmarks. The project risks becoming a redundant synthetic benchmark unless it demonstrates a clearly distinct intervention-control construct or yields a meaningful negative/replication result.

## Mitigations

Independent annotation and preserved raw labels; acceptable-action sets where justified; leakage tests and shuffled-feature controls; preregistered utility profiles/stopping rules; protected one-shot evaluation; cross-domain and temporal tests; explicit negative-result reporting.
