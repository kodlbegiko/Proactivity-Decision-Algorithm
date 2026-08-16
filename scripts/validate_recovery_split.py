#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

DATA = Path("data/recovery_v3_dev_ood")
ACTIONS = {"ACT", "ASK", "IGNORE", "NOTIFY", "SUGGEST", "WAIT"}


def load(name):
    return [json.loads(x) for x in (DATA / name).read_text(encoding="utf-8").splitlines() if x.strip()]


def main():
    public = {s: load(f"{s}.jsonl") for s in ("train", "validation", "ood")}
    private = {s: load(f"{s}_private.jsonl") for s in ("train", "validation", "ood")}
    ids = {s: {r["source_state_id"] for r in private[s]} for s in private}
    assert ids["train"].isdisjoint(ids["validation"])
    assert ids["train"].isdisjoint(ids["ood"])
    assert ids["validation"].isdisjoint(ids["ood"])
    for split, rows in public.items():
        assert all(r["development_status"] == "DEVELOPMENT_ONLY" for r in rows)
        assert all(r["split"] == split for r in rows)
        assert set(r["gold_action"] for r in rows) == ACTIONS
        counts = Counter(r["gold_action"] for r in rows)
        assert len(set(counts.values())) == 1, (split, counts)
        assert {r["source_state_id"] for r in rows} == ids[split]
    cf = load("counterfactual_relations.jsonl"); inv = load("invariance_relations.jsonl")
    assert all(r["development_status"] == "DEVELOPMENT_ONLY" for r in cf + inv)
    assert all(r["left"]["gold_action"] != r["right"]["gold_action"] for r in cf)
    assert len(cf) >= 1 and len(inv) >= 1
    print("RECOVERY V3 GROUP-AWARE SPLIT AUDIT = PASS")


if __name__ == "__main__":
    main()
