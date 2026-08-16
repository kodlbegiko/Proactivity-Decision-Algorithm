from __future__ import annotations
import re
from collections import Counter,defaultdict
from .agreement import LEGAL_ACTIONS,cohen_kappa_diagnostic,confusion_matrix,per_class_agreement,raw_agreement
from .annotations import Annotation
from ..decisions import Decision,is_intervention

def align(a:list[Annotation],b:list[Annotation]):
    am={x.scenario_id:x for x in a}; bm={x.scenario_id:x for x in b}
    if len(am)!=len(a) or len(bm)!=len(b): raise ValueError("duplicate scenario_id")
    if set(am)!=set(bm): raise ValueError("annotation scenario sets differ")
    ids=sorted(am)
    if not ids: raise ValueError("no annotation rows")
    return ids,am,bm

def acceptable_action_report(ids,am,bm):
    j=[]; apb=bpa=mutual=0
    for sid in ids:
        sa,sb=am[sid].acceptable_actions,bm[sid].acceptable_actions; union=sa|sb
        j.append(len(sa&sb)/len(union)); ai=am[sid].preferred_action in sb; bi=bm[sid].preferred_action in sa; apb+=ai; bpa+=bi; mutual+=ai and bi
    n=len(ids); return {"mean_jaccard":sum(j)/n,"a_preferred_accepted_by_b":apb/n,"b_preferred_accepted_by_a":bpa/n,"mutual_acceptability_rate":mutual/n}

def core_class_report(ids,am,bm,pair):
    wanted={Decision(pair[0]),Decision(pair[1])}; subset=[sid for sid in ids if am[sid].preferred_action in wanted and bm[sid].preferred_action in wanted]
    if not subset: return {"pair":list(pair),"n":0,"exact_pair_agreement":None,"mutual_confusion_rate":None,"directional_confusion":{},"threshold":"NO NUMERIC CORE-COLLAPSE THRESHOLD FROZEN"}
    exact=sum(am[s].preferred_action==bm[s].preferred_action for s in subset); directional=Counter(f"{am[s].preferred_action.value}->{bm[s].preferred_action.value}" for s in subset if am[s].preferred_action!=bm[s].preferred_action)
    return {"pair":list(pair),"n":len(subset),"exact_pair_agreement":exact/len(subset),"mutual_confusion_rate":1-exact/len(subset),"directional_confusion":dict(sorted(directional.items())),"threshold":"NO NUMERIC CORE-COLLAPSE THRESHOLD FROZEN"}

def reliability_report(a:list[Annotation],b:list[Annotation],sources:dict|None=None):
    ids,am,bm=align(a,b); la=[am[i].preferred_action.value for i in ids]; lb=[bm[i].preferred_action.value for i in ids]; k,w=cohen_kappa_diagnostic(la,lb)
    out={"n":len(ids),"raw_agreement":raw_agreement(la,lb),"cohen_kappa":k,"cohen_kappa_warning":w,"per_class_agreement":per_class_agreement(la,lb),"confusion_matrix_a_rows_b_columns":confusion_matrix(la,lb),"acceptable_actions":acceptable_action_report(ids,am,bm),"ambiguity_rate_a":sum(am[i].ambiguity_flag for i in ids)/len(ids),"ambiguity_rate_b":sum(bm[i].ambiguity_flag for i in ids)/len(ids),"either_annotator_ambiguity_rate":sum(am[i].ambiguity_flag or bm[i].ambiguity_flag for i in ids)/len(ids),"confidence_distribution_a":dict(sorted(Counter(am[i].confidence for i in ids).items())),"confidence_distribution_b":dict(sorted(Counter(bm[i].confidence for i in ids).items())),"core_classes":{"IGNORE_vs_WAIT":core_class_report(ids,am,bm,("IGNORE","WAIT")),"ASK_vs_ACT":core_class_report(ids,am,bm,("ASK","ACT"))}}
    if sources:
        if set(ids)!=set(sources): raise ValueError("source and annotation scenario sets differ")
        groups=defaultdict(list)
        for sid in ids: groups[sources[sid]["domain"]].append(sid)
        by={}
        for domain,dids in sorted(groups.items()):
            da=[am[i].preferred_action.value for i in dids]; db=[bm[i].preferred_action.value for i in dids]; dk,dw=cohen_kappa_diagnostic(da,db)
            by[domain]={"n":len(dids),"raw_agreement":raw_agreement(da,db),"cohen_kappa":dk,"warning":dw or ("SMALL_CELL_INTERPRET_WITH_CAUTION" if len(dids)<30 else None),"ambiguity_rate":sum(am[i].ambiguity_flag or bm[i].ambiguity_flag for i in dids)/len(dids)}
        out["domain_reliability"]=by
    return out

def disagreement_report(a:list[Annotation],b:list[Annotation]):
    ids,am,bm=align(a,b); pairs=Counter(); reasons=Counter(); ignore_int=wait_int=0
    for sid in ids:
        aa,bb=am[sid],bm[sid]
        if aa.preferred_action==bb.preferred_action: continue
        key=" vs ".join(sorted((aa.preferred_action.value,bb.preferred_action.value))); pairs[key]+=1
        for code in {aa.reason_code,bb.reason_code}:
            if code=="permission": reasons["permission_disagreements"]+=1
            elif code in {"timing","delay_cost"}: reasons["timing_disagreements"]+=1
            elif code=="risk": reasons["risk_disagreements"]+=1
            elif code in {"missing_context","stale_context"}: reasons["context_sufficiency_disagreements"]+=1
        x,y=aa.preferred_action,bb.preferred_action
        ignore_int+=(x==Decision.IGNORE and is_intervention(y)) or (y==Decision.IGNORE and is_intervention(x)); wait_int+=(x==Decision.WAIT and is_intervention(y)) or (y==Decision.WAIT and is_intervention(x))
    named={"IGNORE_vs_WAIT":pairs.get("IGNORE vs WAIT",0),"WAIT_vs_SUGGEST":pairs.get("SUGGEST vs WAIT",0),"SUGGEST_vs_NOTIFY":pairs.get("NOTIFY vs SUGGEST",0),"NOTIFY_vs_ASK":pairs.get("ASK vs NOTIFY",0),"ASK_vs_ACT":pairs.get("ACT vs ASK",0)}
    return {"n":len(ids),"disagreements":sum(pairs.values()),"confusion_taxonomy":dict(pairs.most_common()),"named_adjacent_confusions":named,"ignore_vs_intervention":ignore_int,"wait_vs_immediate_intervention":wait_int,**reasons,"causal_diagnosis":"DESCRIPTIVE_ONLY_NO_HIDDEN_DESIGN_INTENT_USED"}

def counterfactual_report(a:list[Annotation],b:list[Annotation],meta:dict):
    ids,am,bm=align(a,b); groups=defaultdict(list)
    for sid in ids:
        m=meta.get(sid,{})
        if m.get("pair_id"): groups[m["pair_id"]].append((int(m["pair_variant"]),sid))
    ta=[]; tb=[]
    for pid,members in sorted(groups.items()):
        if len(members)!=2: raise ValueError(f"counterfactual pair {pid} does not have 2 members")
        members.sort(); s0,s1=members[0][1],members[1][1]; ta.append((am[s0].preferred_action.value,am[s1].preferred_action.value)); tb.append((bm[s0].preferred_action.value,bm[s1].preferred_action.value))
    if not ta: return {"pairs_tested":0}
    ac=[x!=y for x,y in ta]; bc=[x!=y for x,y in tb]
    return {"pairs_tested":len(ta),"annotator_a_changed_label_rate":sum(ac)/len(ac),"annotator_b_changed_label_rate":sum(bc)/len(bc),"cross_annotator_exact_transition_rate":sum(x==y for x,y in zip(ta,tb))/len(ta),"cross_annotator_change_status_agreement":sum(x==y for x,y in zip(ac,bc))/len(ac),"uses_hidden_expected_label":False}

def temporal_report(a:list[Annotation],b:list[Annotation],meta:dict):
    ids,am,bm=align(a,b); groups=defaultdict(list); rows={}; exact=stage_ok=stages=0
    for sid in ids:
        m=meta.get(sid,{})
        if m.get("sequence_id"): groups[m["sequence_id"]].append((int(m["sequence_stage"]),sid))
    for seq,members in sorted(groups.items()):
        members.sort(); la=[am[s].preferred_action.value for _,s in members]; lb=[bm[s].preferred_action.value for _,s in members]; exact+=la==lb; stage_ok+=sum(x==y for x,y in zip(la,lb)); stages+=len(la); rows[seq]={"annotator_a":la,"annotator_b":lb,"exact_match":la==lb}
    return {"sequences":len(groups),"cross_annotator_stage_agreement":None if not stages else stage_ok/stages,"exact_sequence_pattern_rate":None if not groups else exact/len(groups),"sequence_labels":rows,"monotonicity_forced":False}

def lexical_leakage_report(annotations:list[Annotation],sources:dict,min_support:int=3):
    am={a.scenario_id:a for a in annotations}
    if set(am)!=set(sources): raise ValueError("source and annotation scenario sets differ")
    global_counts=Counter(a.preferred_action.value for a in annotations); n=len(annotations); gp={k:v/n for k,v in global_counts.items()}; feats=defaultdict(Counter)
    for sid,a in am.items():
        toks=re.findall(r"[a-z0-9_]+",sources[sid]["scenario_context"].lower()); fs=set(toks)|{f"{x} {y}" for x,y in zip(toks,toks[1:])}
        for f in fs: feats[f][a.preferred_action.value]+=1
    construction={"revised","contextual","difference","conditions","concerns","step","observation"}; legitimate={"permission","authorized","completed","acknowledged","stale","urgent","deadline","conflicts","confirmation"}; out=[]
    for token,counts in feats.items():
        support=sum(counts.values())
        if support<min_support: continue
        dist={k:counts.get(k,0)/support for k in LEGAL_ACTIONS}; strength=.5*sum(abs(dist.get(k,0)-gp.get(k,0)) for k in LEGAL_ACTIONS); words=set(token.split()); cls="POSSIBLE_GENERATION_SHORTCUT" if words&construction else "LEGITIMATE_SIGNAL" if words&legitimate else "REQUIRES_MANUAL_REVIEW"
        out.append({"token":token,"support":support,"label_distribution":dict(counts),"association_strength":strength,"classification":cls})
    out.sort(key=lambda r:(-r["association_strength"],-r["support"],r["token"])); return {"status":"EXECUTED_ON_PROVIDED_LABELS","features":out,"automatic_removal":False}

def metadata_leakage_report(annotations:list[Annotation],sources:dict,meta:dict):
    am={a.scenario_id:a for a in annotations}; ids=sorted(am)
    if set(ids)!=set(sources): raise ValueError("source and annotation scenario sets differ")
    def purity(vals):
        buckets=defaultdict(Counter)
        for sid in ids: buckets[str(vals[sid])][am[sid].preferred_action.value]+=1
        total=sum(sum(c.values()) for c in buckets.values()); return {"levels":len(buckets),"weighted_label_purity":sum(max(c.values()) for c in buckets.values())/total}
    features={"domain":{sid:sources[sid]["domain"] for sid in ids},"timestamp_hour":{sid:sources[sid]["timestamp"][11:13] for sid in ids},"generation_family":{sid:meta.get(sid,{}).get("design_category","unknown") for sid in ids},"counterfactual_identity":{sid:meta.get(sid,{}).get("pair_id","none") for sid in ids},"sequence_position":{sid:meta.get(sid,{}).get("sequence_stage","none") for sid in ids}}
    return {"scenario_id":"PROHIBITED_IDENTIFIER_HIGH_CARDINALITY_NOT_INTERPRETED_AS_SIGNAL","row_order":"CHECK_WITH_SHUFFLE_CONTROL","features":{k:purity(v) for k,v in features.items()},"hidden_metadata_policy_visible":False}
