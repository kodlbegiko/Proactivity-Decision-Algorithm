#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from proactivity.recovery_candidates_v3 import CANDIDATE_FACTORIES

EXPECTED = ["V3A_factor_linear_c1", "V3A_factor_linear_c4", "V3A_factor_tree", "V3C_text_lr_c1", "V3C_text_lr_c4", "V3C_text_svc", "V3D_hybrid_c1", "V3D_hybrid_c4"]


def main():
    assert list(CANDIDATE_FACTORIES) == EXPECTED, list(CANDIDATE_FACTORIES)
    report = json.loads(Path("reports/recovery_v3/candidate_search_results.json").read_text(encoding="utf-8"))
    assert report["candidate_budget"] == 8
    assert report["candidates_executed"] == 8
    assert [r["name"] for r in report["candidates"]] == EXPECTED
    assert report["selected_candidate"] == "V3A_factor_tree"
    assert sum(bool(r["eligible"]) for r in report["candidates"]) == 1
    print("RECOVERY V3 PREREGISTERED SEARCH BUDGET = PASS (8/8; no hidden candidates)")


if __name__ == "__main__":
    main()
