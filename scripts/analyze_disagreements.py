from __future__ import annotations
import argparse, json
from collections import Counter
from proactivity.evaluation.annotations import load_annotations

p=argparse.ArgumentParser(); p.add_argument("a"); p.add_argument("b"); args=p.parse_args()
a={x.scenario_id:x for x in load_annotations(args.a)}; b={x.scenario_id:x for x in load_annotations(args.b)}
ids=sorted(set(a)&set(b)); pairs=Counter()
for i in ids:
    if a[i].preferred_action!=b[i].preferred_action:
        pair=" vs ".join(sorted([a[i].preferred_action.value,b[i].preferred_action.value])); pairs[pair]+=1
print(json.dumps({"disagreements":sum(pairs.values()),"taxonomy":dict(pairs.most_common())},indent=2))
