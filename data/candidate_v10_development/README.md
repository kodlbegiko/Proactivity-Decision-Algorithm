# Candidate-v10 Development Data

The JSONL datasets in this directory are deterministically materialized by `python -m benchmark_v10.run_development` from preregistered Candidate-v10 seeds before qualification metrics are computed. The Candidate-v10 mission workflow commits the materialized JSONL files and `manifest.json` back to this branch as frozen development evidence.

Candidate-v9 H1 individual records are neither read nor reused.
