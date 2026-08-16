from __future__ import annotations
import inspect,json,random
from candidate_v11.model import CandidateArchitecture,CompositionalParser,PrototypeParser,Proposition,Resolution,act_allowed,decide_action,valid_state,FACTOR_DEFINITIONS
from candidate_v11.evidence import EvidenceGraph
from benchmark_v11.generator import BASE_STATES,ROOTS,render_proposition,render_state,generate_suite,dataset_digest

def pred_for(state,name="V11-C",group="train",suite="compositional"):
    return CandidateArchitecture(name).predict(render_state(dict(state),random.Random(7),root_group=group,suite=suite))
def test_01_normative_invalid_state_prevention():
    s=dict(BASE_STATES["ACT"]);s["permission"]="not_required";assert not valid_state(s)
def test_02_external_permission_act_invariant():
    s=dict(BASE_STATES["ACT"]);s["permission"]="missing";assert not act_allowed(s,set())
def test_03_local_permission_invariant():
    s=dict(BASE_STATES["ACT"]);s["side_effect"]="local";s["permission"]="missing";assert not act_allowed(s,set())
def test_04_information_invariant():
    s=dict(BASE_STATES["ACT"]);s["information"]="insufficient";assert not act_allowed(s,set())
def test_05_low_risk_invariant():
    s=dict(BASE_STATES["ACT"]);s["risk"]="medium";assert not act_allowed(s,set())
def test_06_reversibility_invariant():
    s=dict(BASE_STATES["ACT"]);s["reversibility"]="irreversible";assert not act_allowed(s,set())
def test_07_execution_invariant():
    s=dict(BASE_STATES["ACT"]);s["execution_possible"]=False;assert not act_allowed(s,set())
def test_08_material_need_invariant():
    s=dict(BASE_STATES["ACT"]);s["need"]="optional";assert not act_allowed(s,set())
def test_09_completed_invariant():
    s=dict(BASE_STATES["ACT"]);s["completed"]=True;assert decide_action(s,set())=="IGNORE"
def test_10_negation():
    p=CompositionalParser().parse(render_proposition("information","insufficient","facts",negated=True))[0];assert p.value=="sufficient"
def test_11_double_negation_semantic_inverse():
    p=CompositionalParser().parse(render_proposition("execution_possible",False,"execute",negated=True))[0];assert p.value is True
def test_12_modal_uncertainty():
    p=CompositionalParser().parse(render_proposition("risk","low","risk",certainty="uncertain"))[0];assert p.certainty=="uncertain"
def test_13_direct_contradiction():
    p=CandidateArchitecture("V11-C").predict(render_proposition("risk","low","risk")+"\n"+render_proposition("risk","high","hazard"));assert p.beliefs["risk"].resolution==Resolution.CONTRADICTORY
def test_14_paraphrastic_contradiction():
    p=CandidateArchitecture("V11-C").predict(render_proposition("risk","low","peril")+"\n"+render_proposition("risk","high","jeopardy",syntax="subordinate"));assert p.beliefs["risk"].resolution==Resolution.CONTRADICTORY
def test_15_cross_scope_non_contradiction():
    s=dict(BASE_STATES["ACT"]);text=render_state(s,random.Random(1),root_group="stress",suite="compositional")+"\n"+render_proposition("permission","missing","assent",scope="local_action");p=CandidateArchitecture("V11-C").predict(text);assert p.beliefs["permission"].value=="granted" and not p.contradiction_detected
def test_16_supersession():
    a=render_proposition("permission","missing","consent",scope="external_action",prefix="Earlier evidence:");b=render_proposition("permission","granted","approval",scope="external_action",prefix="A later correction replaces the earlier statement.");p=CandidateArchitecture("V11-C").predict(a+"\n"+b);assert p.beliefs["permission"].value=="granted"
def test_17_temporal_precedence():
    a=render_proposition("risk","high","risk",prefix="Earlier evidence:");b=render_proposition("risk","low","hazard",prefix="A later correction replaces the earlier statement.");p=CandidateArchitecture("V11-C").predict(a+"\n"+b);assert not p.contradiction_detected and p.beliefs["risk"].value=="low"
def test_18_conditional_scope():
    g=EvidenceGraph.build([Proposition("risk","low",condition="A",sequence=0),Proposition("risk","high",condition="B",sequence=1)]);assert any(e.relation=="conditional_on" for e in g.edges)
def test_19_lexical_root_disjoint_parsing():
    p=CompositionalParser().parse(render_proposition("permission","granted","assent",scope="external_action"))[0];assert p.factor=="permission" and p.value=="granted"
def test_20_semantic_paraphrase():
    p=CompositionalParser().parse(render_proposition("risk","low","peril",syntax="passive"))[0];assert p.factor=="risk" and p.value=="low"
def test_21_cross_factor_distractor():
    s=dict(BASE_STATES["ACT"]);text=render_state(s,random.Random(2),root_group="stress",suite="compositional")+"\nBackground note mentions exposure to an adverse outcome or harm but provides no classified status.";p=CandidateArchitecture("V11-C").predict(text);assert p.beliefs["risk"].value=="low"
def test_22_counterfactual_permission_removal():
    a=dict(BASE_STATES["ACT"]);b=dict(a);b["permission"]="missing";assert decide_action(a,set())=="ACT" and decide_action(b,set())!="ACT"
def test_23_counterfactual_risk_increase():
    a=dict(BASE_STATES["ACT"]);b=dict(a);b["risk"]="high";assert decide_action(a,set())=="ACT" and decide_action(b,set())!="ACT"
def test_24_counterfactual_info_degradation():
    a=dict(BASE_STATES["ACT"]);b=dict(a);b["information"]="insufficient";assert decide_action(a,set())=="ACT" and decide_action(b,set())!="ACT"
def test_25_counterfactual_execution_disable():
    a=dict(BASE_STATES["ACT"]);b=dict(a);b["execution_possible"]=False;assert decide_action(a,set())=="ACT" and decide_action(b,set())!="ACT"
def test_26_no_false_certainty():
    p=CandidateArchitecture("V11-C").predict(render_proposition("risk","low","risk",certainty="uncertain"));assert p.beliefs["risk"].resolution==Resolution.UNKNOWN
def test_27_act_blocked_on_unknown():assert not act_allowed(dict(BASE_STATES["ACT"]),{"risk"})
def test_28_act_blocked_on_contradictory():assert not act_allowed(dict(BASE_STATES["ACT"]),{"permission"})
def test_29_deterministic_prediction():
    text=render_state(dict(BASE_STATES["ACT"]),random.Random(3),root_group="stress",suite="compositional");a=CandidateArchitecture("V11-C").predict(text);b=CandidateArchitecture("V11-C").predict(text);assert a.action==b.action and a.policy_state==b.policy_state
def test_30_deterministic_training_generator():
    a=generate_suite("validation",12,seed=4242);b=generate_suite("validation",12,seed=4242);assert dataset_digest(a)==dataset_digest(b)
def test_31_model_serialization():
    p=pred_for(BASE_STATES["ACT"]);payload={"action":p.action,"state":p.policy_state};assert json.loads(json.dumps(payload,sort_keys=True))==payload
def test_32_split_disjointness():
    groups=list(ROOTS.values())
    for factor in FACTOR_DEFINITIONS:
        sets=[set(g[factor]) for g in groups]
        for i in range(len(sets)):
            for j in range(i+1,len(sets)):assert sets[i].isdisjoint(sets[j])
def test_33_seed_immutability():
    a=generate_suite("lexical_abstraction",5,seed=111003);b=generate_suite("lexical_abstraction",5,seed=111003);assert dataset_digest(a)==dataset_digest(b)
def test_34_collapse_audit_reachability():assert {decide_action(dict(s),set()) for s in BASE_STATES.values()}==set(BASE_STATES)
def test_35_candidate_v10_integrity_boundary():
    import candidate_v11.model as m;src=inspect.getsource(m).lower();assert "candidate_v10" not in src and "data/candidate_v10_development" not in src
def test_36_prototype_unseen_root():
    p=PrototypeParser().parse(render_proposition("risk","low","peril",syntax="subordinate"))[0];assert p.factor=="risk" and p.value=="low"
def test_37_graph_support():assert EvidenceGraph.build([Proposition("risk","low",sequence=0),Proposition("risk","low",sequence=1)]).edges_for("supports")
def test_38_graph_contradiction():assert EvidenceGraph.build([Proposition("risk","low",sequence=0),Proposition("risk","high",sequence=1)]).edges_for("contradicts")
def test_39_graph_supersession():assert EvidenceGraph.build([Proposition("risk","high",sequence=0),Proposition("risk","low",sequence=1,supersedes_previous=True)]).edges_for("supersedes")
def test_40_safe_projection_valid():
    p=CandidateArchitecture("V11-C").predict(render_proposition("risk","low","risk",certainty="uncertain"));assert not p.invalid_state
