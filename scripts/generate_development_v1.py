from __future__ import annotations
import csv, hashlib, json, random
from pathlib import Path

DOMAINS = {
"study": ("coursework", ["lab report","calculus quiz","chemistry worksheet","reading response","group presentation","field notebook","practice exam","research outline","problem set","essay draft","data table","seminar notes"]),
"work": ("project", ["client brief","release checklist","budget sheet","design review","vendor quote","meeting deck","QA report","issue tracker","handoff note","forecast model","contract draft","launch plan"]),
"scheduling": ("calendar", ["advisor meeting","team sync","appointment","deadline block","interview slot","workshop","office hour","training session","review call","reservation","presentation time","exam schedule"]),
"communication": ("message", ["advisor email","team message","family update","client reply","group chat","support ticket","class announcement","vendor note","registration notice","travel message","project comment","confirmation email"]),
"device": ("device", ["backup job","software update","battery alert","sync conflict","storage warning","network change","security notice","print queue","cloud upload","system restart","file export","account session"]),
"travel": ("trip", ["train booking","flight gate","hotel check-in","bus transfer","museum ticket","route change","weather notice","seat reservation","luggage rule","airport transfer","rail pass","event entry"]),
}
CATS=["critical_intervention","useful_noncritical","premature_intervention","redundant_intervention","distracting_intervention","ambiguous_context","unsafe_autonomy","false_urgency","delayed_benefit","conflicting_signals","stale_context","already_completed"]
PAIR_VARS=["interruptibility","permission_evidence","confidence","acknowledgement"]
WORDS=["amber","birch","cedar","delta","ember","fern","granite","harbor","iris","juniper","kelp","linen","maple","nectar","opal","pebble","quartz","reed","spruce","tulip","umber","violet","willow","zephyr"]

def uid(domain, kind, slot):
    return "dv1-"+hashlib.sha256(f"{domain}|{kind}|{slot}".encode()).hexdigest()[:12]

def scalars(di, slot):
    return {
      "workload": round(.15 + ((slot*7+di*3)%70)/100,2),
      "interruptibility": round(.12 + ((slot*11+di*5)%76)/100,2),
      "importance": round(.22 + ((slot*13+di*7)%72)/100,2),
      "urgency": round(.10 + ((slot*17+di*2)%82)/100,2),
      "confidence": round(.45 + ((slot*9+di*4)%50)/100,2),
      "risk": round(((slot*5+di*9)%75)/100,2),
      "delay": round(((slot*19+di*6)%88)/100,2),
      "fresh": round(.50 + ((slot*3+di*8)%50)/100,2),
    }

def record(domain, di, slot, summary, facts, history=None, permission="not_applicable", kind="independent"):
    s=scalars(di,slot); sid=uid(domain,kind,slot)
    perm_required=permission in {"required_not_granted","unclear"}; perm_granted=permission=="granted"
    if perm_granted: perm_required=True
    return {
      "scenario_id":sid,"timestamp":f"2026-08-{14+di:02d}T{8+(slot%10):02d}:{(slot*7)%60:02d}:00Z","domain":domain,
      "raw_context":{"current_activity":f"Working on {DOMAINS[domain][0]} while {WORDS[(slot+di)%len(WORDS)]} focus is active.",
        "event_summary":summary,"observable_facts":facts,"recent_history":history or [],
        "permission_evidence":permission,"time_context":f"Observation window {WORDS[(slot*2+di)%len(WORDS)]}.","source_kind":"system_observation"},
      "user_state":{"activity":DOMAINS[domain][0],"workload":s["workload"],"interruptibility":s["interruptibility"]},
      "event":{"type":kind,"importance":s["importance"],"urgency":s["urgency"],"deadline_seconds":None if slot%5==0 else 600+slot*173,"confidence":s["confidence"],"evidence_reliability":round(min(.99,s["confidence"]+.03),2)},
      "task_state":{"status":"open","acknowledged":False,"completed":False},"history":[],
      "action_risk":s["risk"],"reversibility":round(1-s["risk"]*.7,2),"expected_delay_cost":s["delay"],
      "permission_required":perm_required,"permission_granted":perm_granted,"context_freshness":s["fresh"],
      "candidate_decisions":["IGNORE","WAIT","SUGGEST","NOTIFY","ASK","ACT"]}

def build():
    rows=[]; meta=[]
    for di,(domain,(_,topics)) in enumerate(DOMAINS.items()):
        for slot in range(12):
            topic=topics[slot]; cat=CATS[slot]
            summary=f"A {topic} changed in a way relevant to the current {domain} context."
            facts=[
              f"The observed item is {topic}, described through the {WORDS[(slot+3*di)%24]} channel.",
              f"The user state contains {WORDS[(slot*3+di)%24]} evidence and a distinct {domain} constraint.",
              f"The latest observation differs from the prior {WORDS[(slot*5+2*di)%24]} state."
            ]
            if cat=="redundant_intervention": facts.append("The user has already acknowledged the same update.")
            if cat=="already_completed": facts.append("The underlying task is already completed.")
            if cat=="stale_context": facts.append("The only supporting observation is older than the current state.")
            if cat=="ambiguous_context": facts.append("Two observed sources disagree about the relevant fact.")
            if cat=="unsafe_autonomy": facts.append("No explicit authorization to perform the consequential action is recorded.")
            if cat=="false_urgency": facts.append("The source uses urgent wording but the actual schedule remains unchanged.")
            r=record(domain,di,slot,summary,facts,kind="independent")
            if cat=="redundant_intervention": r["task_state"]["acknowledged"]=True
            if cat=="already_completed": r["task_state"].update(status="completed",completed=True,acknowledged=True)
            rows.append(r); meta.append({"scenario_id":r["scenario_id"],"design_category":cat})
        for p,var in enumerate(PAIR_VARS):
            slot=12+p*2; topic=topics[p+2]; pid=f"cf-{domain}-{p+1}"
            basefacts=[f"The {topic} has a new confirmed state from a domain-specific source.",
                       f"Other observed {domain} conditions remain unchanged.",
                       f"A {WORDS[(p+di+7)%24]} contextual detail is the only material difference in this observation."]
            for v in (0,1):
                facts=list(basefacts); perm="not_applicable"
                if var=="interruptibility": facts.append("The user is in a low-interruption focus block." if v==0 else "The user is between tasks and can be interrupted.")
                elif var=="permission_evidence":
                    perm="required_not_granted" if v==0 else "granted"; facts.append("No permission to perform the action is recorded." if v==0 else "The user previously authorized this exact action class.")
                elif var=="confidence": facts.append("The observation is unconfirmed and conflicts with one source." if v==0 else "Two independent sources confirm the same observation.")
                elif var=="acknowledgement": facts.append("The user has not acknowledged the update." if v==0 else "The user already acknowledged this exact update.")
                r=record(domain,di,slot+v,f"A revised {topic} observation is relevant to the current {domain} situation.",facts,permission=perm,kind="counterfactual")
                if var=="interruptibility": r["user_state"]["interruptibility"]=.08 if v==0 else .92
                if var=="confidence": r["event"]["confidence"]=r["event"]["evidence_reliability"]=.35 if v==0 else .96
                if var=="acknowledgement": r["task_state"]["acknowledged"]=bool(v)
                rows.append(r); meta.append({"scenario_id":r["scenario_id"],"design_category":"counterfactual","pair_id":pid,"pair_variant":v,"changed_variable":var,"intended_relation":"single_variable_sensitivity"})
        seq=f"seq-{domain}-1"; topic=topics[-1]
        stages=[
          ("Initial observation arrives with time remaining.",["No prior notification has been sent."]),
          ("The same event moves materially closer.",["No acknowledgement is recorded yet."]),
          ("The user acknowledges the update.",["Acknowledgement is now recorded."]),
          ("The underlying task is completed.",["Completion is now recorded and the event no longer requires follow-up."])
        ]
        for st,(summary,extra) in enumerate(stages):
            slot=20+st
            facts=[f"The current event concerns {topic} in the {domain} domain.",*extra,f"The latest observable detail is {WORDS[(st*4+di+9)%24]}."]
            r=record(domain,di,slot,summary,facts,history=[f"An earlier observation at step {st-1} is in recent history."] if st else [],kind="sequence")
            if st>=2: r["task_state"]["acknowledged"]=True
            if st==3: r["task_state"].update(status="completed",completed=True)
            rows.append(r); meta.append({"scenario_id":r["scenario_id"],"design_category":"temporal_sequence","sequence_id":seq,"sequence_stage":st,"transition_type":["initial","escalate","acknowledge","complete"][st]})
    rnd=random.Random(20260813); order=list(range(len(rows))); rnd.shuffle(order)
    return [rows[i] for i in order],[meta[i] for i in order]

def packet_text(r):
    c=r["raw_context"]; parts=[f"Current activity: {c['current_activity']}",f"Event: {c['event_summary']}","Observable facts: "+" | ".join(c["observable_facts"])]
    if c["recent_history"]: parts.append("Recent history: "+" | ".join(c["recent_history"]))
    parts += ["Permission evidence: "+c["permission_evidence"],"Time context: "+c["time_context"]]
    return "\n".join(parts)

def write_packets(root, rows):
    fields=["scenario_id","domain","timestamp","scenario_context","preferred_action","acceptable_actions","confidence","ambiguity_flag","reason_code","criticality","rationale"]
    out=root/"annotation"; out.mkdir(exist_ok=True)
    for name,seed in [("packet_a.csv",111),("packet_b.csv",222)]:
        arr=list(rows); random.Random(seed).shuffle(arr)
        with (out/name).open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
            for r in arr: w.writerow({"scenario_id":r["scenario_id"],"domain":r["domain"],"timestamp":r["timestamp"],"scenario_context":packet_text(r)})

def main():
    root=Path(__file__).resolve().parents[1]; rows,meta=build()
    d=root/"data/development"; d.mkdir(parents=True,exist_ok=True)
    (d/"development_v1.jsonl").write_text("".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in rows),encoding="utf-8")
    (d/"development_v1.meta.jsonl").write_text("".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in meta),encoding="utf-8")
    write_packets(root,rows)
    print(f"generated={len(rows)} domains={len(set(x['domain'] for x in rows))}")

if __name__=="__main__": main()
