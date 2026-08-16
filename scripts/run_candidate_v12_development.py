from __future__ import annotations
import json
from proactivity.candidate_v12_dev import development_summary, mechanistic_diagnostics

if __name__ == "__main__":
    result = development_summary()
    result["mechanistic_diagnostics"] = mechanistic_diagnostics()
    print(json.dumps(result, indent=2, sort_keys=True))
