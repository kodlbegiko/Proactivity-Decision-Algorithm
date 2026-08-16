from __future__ import annotations
import argparse,json
from proactivity.evaluation.annotations import validate_completed_annotations
p=argparse.ArgumentParser(); p.add_argument("completed"); p.add_argument("blank_packet"); args=p.parse_args()
print(json.dumps(validate_completed_annotations(args.completed,args.blank_packet),indent=2,sort_keys=True))
