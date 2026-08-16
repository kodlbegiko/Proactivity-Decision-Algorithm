from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from .model import Proposition, FactorBelief, Resolution, FACTORS

@dataclass(frozen=True)
class EvidenceEdge:
    source: int
    target: int
    relation: str

@dataclass
class EvidenceGraph:
    nodes: list[Proposition] = field(default_factory=list)
    edges: list[EvidenceEdge] = field(default_factory=list)
    RELATIONS = {"supports", "contradicts", "supersedes", "refines", "scopes", "conditional_on"}

    @classmethod
    def build(cls, propositions: Sequence[Proposition]) -> "EvidenceGraph":
        g=cls(nodes=list(propositions))
        for i,a in enumerate(g.nodes):
            for j,b in enumerate(g.nodes):
                if i>=j or a.factor!=b.factor: continue
                if a.scope!=b.scope and a.scope!="general" and b.scope!="general":
                    g.edges.append(EvidenceEdge(i,j,"scopes")); continue
                if b.supersedes_previous and b.sequence>a.sequence:
                    g.edges.append(EvidenceEdge(j,i,"supersedes")); continue
                if a.condition and b.condition and a.condition!=b.condition:
                    g.edges.append(EvidenceEdge(i,j,"conditional_on")); continue
                if a.value is not None and b.value is not None:
                    if a.value==b.value: g.edges.append(EvidenceEdge(i,j,"supports"))
                    elif a.certainty=="asserted" and b.certainty=="asserted": g.edges.append(EvidenceEdge(i,j,"contradicts"))
        return g

    def edges_for(self, relation: str):
        if relation not in self.RELATIONS: raise ValueError(relation)
        return [e for e in self.edges if e.relation==relation]

    def factor_nodes(self,factor: str):
        return [(i,p) for i,p in enumerate(self.nodes) if p.factor==factor]

    def resolve(self, side_effect_value=None):
        beliefs={}; any_contradiction=False; superseded={e.target for e in self.edges if e.relation=="supersedes"}
        for factor in FACTORS:
            indexed=self.factor_nodes(factor)
            if factor=="permission":
                wanted="external_action" if side_effect_value=="external" else "local_action" if side_effect_value=="local" else "general"
                scoped=[x for x in indexed if x[1].scope==wanted]
                if not scoped: scoped=[x for x in indexed if x[1].scope=="general"] or indexed
                indexed=scoped
            else:
                general=[x for x in indexed if x[1].scope=="general"]
                if general: indexed=general
            indexed=[x for x in indexed if x[0] not in superseded]; props=[p for _,p in indexed]
            certain=[(i,p) for i,p in indexed if p.certainty=="asserted" and p.value is not None]
            if not certain:
                beliefs[factor]=FactorBelief(factor,Resolution.UNKNOWN,None,tuple(props),0.0); continue
            values=[]
            for _,p in certain:
                if p.value not in values: values.append(p.value)
            conflict=False
            if len(values)>1:
                ids={i for i,_ in certain}
                conflict=any(e.relation=="contradicts" and e.source in ids and e.target in ids for e in self.edges)
            if conflict:
                beliefs[factor]=FactorBelief(factor,Resolution.CONTRADICTORY,None,tuple(props),1.0); any_contradiction=True
            elif len(values)==1:
                beliefs[factor]=FactorBelief(factor,Resolution.RESOLVED,values[0],tuple(props),1.0)
            else:
                beliefs[factor]=FactorBelief(factor,Resolution.UNRESOLVED,None,tuple(props),0.0)
        return beliefs,any_contradiction
