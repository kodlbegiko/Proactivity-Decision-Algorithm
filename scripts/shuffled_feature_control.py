from __future__ import annotations
import argparse, random
from proactivity.evaluation.annotations import load_annotations
p=argparse.ArgumentParser(); p.add_argument("annotations"); p.add_argument("--seed",type=int,default=42); args=p.parse_args()
labels=load_annotations(args.annotations)
if not labels: raise SystemExit("NO LABELS")
values=[x.preferred_action.value for x in labels]; shuffled=list(values); random.Random(args.seed).shuffle(shuffled)
match=sum(a==b for a,b in zip(values,shuffled))/len(values)
print(f"n={len(values)} shuffled_label_self_match={match:.6f} seed={args.seed}")
