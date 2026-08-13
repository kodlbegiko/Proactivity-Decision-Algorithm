# Annotation packet

The two blinded packets are generated deterministically from the canonical generator rather than stored as opaque binary artifacts:

```bash
python scripts/generate_development_v1.py
sha256sum -c data/development/development_v1.sha256
```

This materializes:

- `annotation/packet_a.csv`
- `annotation/packet_b.csv`

They contain the same 144 scenarios in different deterministic orders. Give packet A and packet B to two genuinely independent human annotators. Packet text is generated from the **raw-context projection only**; researcher-derived scalar state and hidden design metadata are excluded.

After collection, save first-pass files without overwriting them, e.g.:

- `annotations/raw/annotator_a_v1.csv`
- `annotations/raw/annotator_b_v1.csv`

Then record SHA-256 and run:

```bash
PYTHONPATH=src python scripts/compute_agreement.py annotations/raw/annotator_a_v1.csv annotations/raw/annotator_b_v1.csv
PYTHONPATH=src python scripts/analyze_disagreements.py annotations/raw/annotator_a_v1.csv annotations/raw/annotator_b_v1.csv
```

LLM-generated duplicate labels are **not** a substitute for independent human annotation.
