from proactivity import candidate_v11 as c
from benchmark_v11 import generator as g
from benchmark_v11 import evaluation as e

def test_protocol_action_safety():
    s={"permission":"granted","information":"sufficient","urgency":"normal","need":"material","side_effect":"external","risk":"low","reversibility":"reversible","deferral_available":False,"execution_possible":True,"clarification_possible":True,"acknowledged":False,"completed":False}
    assert c.policy_action(s)=="ACT"
    for f,v in [("permission","missing"),("risk","high"),("reversibility","irreversible"),("execution_possible",False)]:
        t=dict(s); t[f]=v; assert c.policy_action(t)!="ACT"

def test_negation_scope_structural():
    text=("approval is granted; information is sufficient; urgency is normal; need is material; sideeffect is external; risk is not high; the action is not irreversible; deferral is unavailable; execution is not impossible; clarification is possible; the issue is unacknowledged; the work is incomplete.")
    out=c.parse(text,"B"); assert out.state["risk"]=="low"; assert out.state["reversibility"]=="reversible"; assert out.state["execution_possible"] is True

def test_scope_correction():
    s=g.valid_state(__import__("random").Random(22)); s["risk"]="low"; text=g.render_state(s,"Scope",9921,1); out=c.parse(text,"B"); assert out.state["risk"]=="low"

def test_counterfactual_exact_pair():
    assert e.paired_metrics(g.counterfactual_pairs(60,7001,4),"B")["counterfactual_exact_pair"]>=0.95

def test_unknown_calibration():
    assert e.unknown_metric(g.unknown_cases(60,7103,4),"B")["legitimate_unknown_recall"]>=0.95

def test_invariance_actions():
    rows=g.make_action_balanced_dataset(5,7207,4)
    for i,r in enumerate(rows[:20]):
        actions={c.parse(t,"B").action for t in g.invariance_texts(r["state"],7300+i)}; assert len(actions)==1

def test_balanced_development_gates():
    m=e.evaluate(g.make_action_balanced_dataset(15,7403,4),"B")
    assert m["fresh_ood_macro_f1"]>=0.88; assert m["exact_latent_state_reconstruction"]>=0.80; assert m["mean_factor_accuracy"]>=0.95; assert m["act_critical_factor_accuracy"]>=0.97
    assert m["critical_unknown_rate"]<=0.05; assert m["act_precision"]>=0.95; assert m["act_recall"]>=0.85; assert m["forbidden_act"]==0; assert m["invalid_action"]==0; assert not m["catastrophic_collapse"]
