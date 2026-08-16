from __future__ import annotations
import argparse,json
from proactivity.evaluation.annotations import archive_raw_annotations
p=argparse.ArgumentParser(); p.add_argument("annotator_a"); p.add_argument("annotator_b"); p.add_argument("packet_a"); p.add_argument("packet_b"); p.add_argument("--out",default="annotations/raw"); args=p.parse_args()
print(json.dumps(archive_raw_annotations(args.annotator_a,args.annotator_b,args.packet_a,args.packet_b,args.out),indent=2,sort_keys=True))
