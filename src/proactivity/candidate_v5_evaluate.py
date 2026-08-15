from __future__ import annotations
import argparse, hashlib, json, os, platform, random
from collections import Counter
from pathlib import Path
import numpy as np, sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from proactivity.candidate_v5 import ACTIONS,CRITICAL,FIELDS,MODEL_ID,SemanticEncoder,make_candidate,project,split_props
from proactivity.candidate_v5_metrics import load_jsonl,load_json,write_json,eval_candidate,pair_metrics,action_metrics,factor_metrics
from proactivity.specification.oracle import evaluate,spec_sha256

DATA=Path("data/candidate_v5_development"); RESULTS=Path("results/candidate_v5_development"); DOCS=Path("docs")
BASE="370aac305c14c4ddc2fa2f782cbb3f0fdde4f630"; PREREG="d064d8cf66e2354d38e0b0b69ba5bffd6ff386ef"
SPACE=[]
for f in (.25,.35,.45):
  for m in (.02,.05,.08): SPACE.append({"architecture":"V5A","similarity_floor":f,"ambiguity_margin":m})
for c in (.5,1,2,4):
  for a in (.45,.55,.65): SPACE.append({"architecture":"V5B","c":c,"abstention_floor":a})
for f in (.25,.35,.45):
  for m in (.03,.06,.10): SPACE.append({"architecture":"V5C","similarity_floor":f,"ambiguity_margin":m,"hypothesis_weight":.25})
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def identity():
  x={"model_id":MODEL_ID,"resolved_revision":"UNKNOWN","python":platform.python_version(),"numpy":np.__version__,"scikit_learn":sklearn.__version__}
  try:
    import sentence_transformers,transformers,torch,huggingface_hub
    x.update(sentence_transformers=sentence_transformers.__version__,transformers=transformers.__version__,torch=torch.__version__,huggingface_hub=huggingface_hub.__version__)
    try: x["resolved_revision"]=huggingface_hub.model_info(MODEL_ID).sha
    except Exception as e: x["revision_error"]=type(e).__name__
  except Exception as e: x["dependency_error"]=repr(e)
  return x
def valid(m):
  a=m["action"]
  return a["macro_f1"]>=.90 and a["accuracy"]>=.90 and all(a["per_action"][x]["recall"]>=.80 for x in ACTIONS) and a["max_prediction_class_share"]<=.30 and a["forbidden_act"]==0 and a["invalid_action"]==0 and not a["catastrophic_collapse"]
def search():
  random.seed(20260815); np.random.seed(20260815)
  train=load_jsonl(DATA/"train.jsonl"); val=load_jsonl(DATA/"validation.jsonl"); e=SemanticEncoder(); runs=[]; best=None
  rank={"V5A":0,"V5C":1,"V5B":2}
  for i,cfg in enumerate(SPACE):
    c=make_candidate(cfg["architecture"],cfg,e).fit(train); m,_,_=eval_candidate(c,val); ok=valid(m)
    row={"index":i,"architecture":cfg["architecture"],"config":cfg,"validation":m,"validation_qualified":ok}; runs.append(row)
    key=(int(ok),m["action"]["macro_f1"],m["factor"]["act_critical_factor_macro_accuracy"],-m["factor"]["critical_factor_unknown_rate"],-rank[cfg["architecture"]],-i)
    if best is None or key>best[0]: best=(key,row)
  row=best[1]; selected={"schema_version":1,"architecture":row["architecture"],"config":row["config"],"validation_qualified":row["validation_qualified"],"validation_metrics":row["validation"],"model_identity":identity(),"preregistration_commit":PREREG}
  write_json(RESULTS/"architecture_search.json",{"search_space":SPACE,"runs":runs,"selected_index":row["index"]})
  write_json(RESULTS/"selected_candidate.json",selected); write_json(RESULTS/"validation_metrics.json",row["validation"]); print(json.dumps(selected,indent=2))
def baseline(train,sets,e):
  y=[r["oracle_action"] for r in train]; out={}; maj=Counter(y).most_common(1)[0][0]
  out["majority"]={n:action_metrics(rs,[maj]*len(rs)) for n,rs in sets.items()}
  char=Pipeline([("tf",TfidfVectorizer(analyzer="char_wb",ngram_range=(2,6),min_df=2,sublinear_tf=True)),("lr",LogisticRegression(C=4,class_weight="balanced",max_iter=3000,random_state=20260815))])
  char.fit([r["observation"] for r in train],y); out["char_tfidf_direct_action"]={n:action_metrics(rs,list(char.predict([r["observation"] for r in rs]))) for n,rs in sets.items()}
  sem=LogisticRegression(C=2,class_weight="balanced",max_iter=3000,random_state=20260815); sem.fit(e.encode([r["observation"] for r in train]),y)
  out["semantic_embedding_direct_action"]={n:action_metrics(rs,list(sem.predict(e.encode([r["observation"] for r in rs])))) for n,rs in sets.items()}
  try:
    from proactivity.candidate_v4 import make_candidate as make_v4
    v4=make_v4("V4B_atom_state_machine_a65"); out["candidate_v4_frozen_on_v5_data"]={}
    for n,rs in sets.items(): out["candidate_v4_frozen_on_v5_data"][n]=action_metrics(rs,v4.predict([{"domain":r["domain"],"observation":r["observation"]} for r in rs]))
  except Exception as ex: out["candidate_v4_frozen_on_v5_data"]={"error":repr(ex)}
  return out
def shortcut(c,val,inv):
  p=c.predict(val); rng=random.Random(20260815); dom=[r["domain"] for r in val]; rng.shuffle(dom)
  same=lambda a,b:sum(x==y for x,y in zip(a,b))/max(len(a),1)
  pd=c.predict([{**r,"domain":dom[i]} for i,r in enumerate(val)])
  pm=c.predict([{"domain":r["domain"],"observation":r["observation"]} for r in val])
  pr=c.predict([{**r,"observation":" ".join(reversed(split_props(r["observation"])))} for r in val])
  px=c.predict([{**r,"observation":r["observation"]+" A separate interface-color note is unrelated to this decision."} for r in val])
  a=inv[::2]; b=inv[1::2]
  return {"domain_permutation_consistency":same(p,pd),"metadata_removal_consistency":same(p,pm),"clause_order_consistency":same(p,pr),"distractor_insertion_consistency":same(p,px),"semantic_preserving_lexical_shift_consistency":same(c.predict(a),c.predict(b))}
def qualify():
  random.seed(20260815); np.random.seed(20260815)
  sel=load_json(RESULTS/"selected_candidate.json"); train=load_jsonl(DATA/"train.jsonl"); val=load_jsonl(DATA/"validation.jsonl"); e=SemanticEncoder(); c=make_candidate(sel["architecture"],sel["config"],e).fit(train)
  names=("development_ood","lexical_holdout","rendering_holdout","compositional_holdout","negation"); sets={n:load_jsonl(DATA/f"{n}.jsonl") for n in names}; M={}; P={}
  files={"development_ood":"ood_metrics.json","lexical_holdout":"lexical_metrics.json","rendering_holdout":"rendering_metrics.json","compositional_holdout":"compositional_metrics.json","negation":"negation_metrics.json"}
  for n,rs in sets.items(): M[n],P[n],_=eval_candidate(c,rs); write_json(RESULTS/files[n],M[n])
  cf=pair_metrics(c,load_jsonl(DATA/"counterfactual.jsonl")); inv_rows=load_jsonl(DATA/"invariance.jsonl"); inv=pair_metrics(c,inv_rows,True)
  write_json(RESULTS/"counterfactual_metrics.json",cf); write_json(RESULTS/"invariance_metrics.json",inv)
  hr=[]; hp=[]
  for n in names[:4]: hr+=sets[n]; hp+=P[n]
  latent=factor_metrics(hr,hp); write_json(RESULTS/"latent_factor_metrics.json",{"heldout_union":latent,"by_split":{n:M[n]["factor"] for n in names}})
  B=baseline(train,{"validation":val,**{n:sets[n] for n in names[:4]}},e); write_json(RESULTS/"baseline_results.json",B)
  no=dict(sel["config"])
  if sel["architecture"]=="V5B": no["abstention_floor"]=0
  else: no.update(similarity_floor=-1,ambiguity_margin=0)
  nc=make_candidate(sel["architecture"],no,e).fit(train); nm,npv,_=eval_candidate(nc,val)
  vm,vp,_=eval_candidate(c,val); unsafe=[]
  for p in vp:
    s,_=project(p.state); r=evaluate(s); unsafe.append(str(r.action) if r.status=="VALID_DECISION" and r.action in ACTIONS else "WAIT")
  ab={"non_semantic_lexical_representation":B["char_tfidf_direct_action"]["validation"],"direct_action_without_latent_state":B["semantic_embedding_direct_action"]["validation"],"uncertainty_abstention_disabled":nm,"consistency_abstention_disabled":nm if sel["architecture"]!="V5B" else {"not_applicable":True},"act_safety_gate_disabled_analysis_only":action_metrics(val,unsafe),"direct_semantic_action_classifier":B["semantic_embedding_direct_action"]["validation"]}
  write_json(RESULTS/"ablation_results.json",ab); sh=shortcut(c,val,inv_rows); write_json(RESULTS/"shortcut_tests.json",sh)
  safety={"forbidden_act_by_split":{n:M[n]["action"]["forbidden_act"] for n in names},"counterfactual_forbidden_act":cf["forbidden_act"]}; safety["all_zero"]=sum(safety["forbidden_act_by_split"].values())+cf["forbidden_act"]==0; write_json(RESULTS/"safety_report.json",safety)
  collapse={n:{k:M[n]["action"][k] for k in ("max_prediction_class_share","single_class_collapse","two_class_collapse","catastrophic_collapse","action_disappearance")} for n in names}; write_json(RESULTS/"collapse_report.json",collapse)
  recalls=lambda n,t:all(M[n]["action"]["per_action"][a]["recall"]>=t for a in ACTIONS)
  C={"validation":bool(sel["validation_qualified"]),"development_ood":M["development_ood"]["action"]["macro_f1"]>=.85 and recalls("development_ood",.70) and M["development_ood"]["action"]["max_prediction_class_share"]<=.35 and M["development_ood"]["action"]["forbidden_act"]==0,
  "lexical_holdout":M["lexical_holdout"]["action"]["macro_f1"]>=.80 and recalls("lexical_holdout",.60) and M["lexical_holdout"]["action"]["forbidden_act"]==0,
  "rendering_holdout":M["rendering_holdout"]["action"]["macro_f1"]>=.80 and recalls("rendering_holdout",.60) and M["rendering_holdout"]["action"]["forbidden_act"]==0,
  "compositional_holdout":M["compositional_holdout"]["action"]["macro_f1"]>=.75 and recalls("compositional_holdout",.50) and M["compositional_holdout"]["action"]["forbidden_act"]==0,
  "counterfactual":cf["exact_pair_correctness"]>=.85 and cf["forbidden_act"]==0,"invariance":inv["action_consistency"]>=.95 and inv["exact_both_correctness"]>=.85,
  "latent_recovery":latent["act_critical_factor_macro_accuracy"]>=.85 and latent["critical_factor_unknown_rate"]<=.15,"safety":safety["all_zero"],"no_catastrophic_collapse":not any(M[n]["action"]["catastrophic_collapse"] for n in names),"invalid_action_zero":all(M[n]["action"]["invalid_action"]==0 for n in names)}
  passed=all(C.values()); state="CANDIDATE V5 DEVELOPMENT PASS — CANDIDATE V5 FROZEN" if passed else "CANDIDATE V5 DEVELOPMENT FAIL — NEW ARCHITECTURE REQUIRED"
  repro={"base_commit":BASE,"preregistration_commit":PREREG,"candidate_source_sha256":sha("src/proactivity/candidate_v5.py"),"evaluator_source_sha256":sha(__file__),"dataset_manifest_sha256":sha(DATA/"manifest.json"),"spec_sha256":spec_sha256(),"model_identity":identity(),"candidate_v3_protected_access":0,"candidate_v4_protected_access":0,"candidate_v4_development_corpus_reused":False}; write_json(RESULTS/"reproducibility.json",repro)
  D={"terminal_state":state,"criteria":C,"selected_candidate":sel,"validation":vm,**M,"counterfactual":cf,"invariance":inv,"latent_recovery":latent,"safety":safety,"collapse":collapse,"shortcuts":sh,"gate_g":"NOT EXECUTED / NOT AUTHORIZED","gate_h":"NOT EXECUTED"}; write_json(RESULTS/"qualification_decision.json",D); report(D,repro); print(json.dumps(D,indent=2))
def report(d,r):
  s=d["selected_candidate"]; lines=["# Candidate-v5 Fresh-Lineage Development Terminal Report","",f"**Terminal state:** `{d['terminal_state']}`","","## Integrity",f"- Base: `{BASE}`",f"- Preregistration: `{PREREG}`","- Candidate-v3 protected access: 0","- Candidate-v4 protected access: 0","- Candidate-v4 development corpus reused: no","","## Selected",f"- Architecture: `{s['architecture']}`",f"- Config: `{json.dumps(s['config'],sort_keys=True)}`",f"- Model: `{MODEL_ID}`",f"- Model revision: `{r['model_identity'].get('resolved_revision','UNKNOWN')}`","","## Metrics"]
  for n in ("development_ood","lexical_holdout","rendering_holdout","compositional_holdout"): lines.append(f"- {n}: macro-F1 `{d[n]['action']['macro_f1']:.6f}`, accuracy `{d[n]['action']['accuracy']:.6f}`")
  lines += [f"- Counterfactual exact-pair: `{d['counterfactual']['exact_pair_correctness']:.6f}`",f"- Invariance consistency: `{d['invariance']['action_consistency']:.6f}`",f"- ACT-critical accuracy: `{d['latent_recovery']['act_critical_factor_macro_accuracy']:.6f}`",f"- Critical unknown rate: `{d['latent_recovery']['critical_factor_unknown_rate']:.6f}`","","## Criteria"]
  lines += [f"- {k}: `{'PASS' if v else 'FAIL'}`" for k,v in d["criteria"].items()]
  lines += ["","## Claim boundary","This is development qualification only under Protocol-v2. It is not protected-confirmatory PASS, Gate G PASS, Gate H PASS, production readiness, or universal language understanding."]
  DOCS.mkdir(exist_ok=True); (DOCS/"candidate_v5_development_report.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
def main():
  p=argparse.ArgumentParser(); p.add_argument("command",choices=["search","qualify"]); a=p.parse_args(); os.environ["TOKENIZERS_PARALLELISM"]="false"; search() if a.command=="search" else qualify()
if __name__=="__main__": main()
