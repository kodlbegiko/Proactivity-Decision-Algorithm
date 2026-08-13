# Annotation packet

`packet_a.csv.gz` and `packet_b.csv.gz` contain the same 144 development-v1 scenarios in different deterministic orders. Materialize them before distribution:

```bash
gzip -dk annotation/packet_a.csv.gz
gzip -dk annotation/packet_b.csv.gz
```

Give packet A and packet B to two genuinely independent human annotators. The packet text is generated from the **raw-context projection only**; researcher-derived scalar state and hidden design metadata are excluded.

After collection, save first-pass files without overwriting them, e.g.:

- `annotations/raw/annotator_a_v1.csv`
- `annotations/raw/annotator_b_v1.csv`

Then record SHA-256 and run:

```bash
PYTHONPATH=src python scripts/compute_agreement.py annotations/raw/annotator_a_v1.csv annotations/raw/annotator_b_v1.csv
PYTHONPATH=src python scripts/analyze_disagreements.py annotations/raw/annotator_a_v1.csv annotations/raw/annotator_b_v1.csv
```

LLM-generated duplicate labels are **not** a substitute for independent human annotation.
