from __future__ import annotations

from collections import Counter
from typing import Sequence

LEGAL_ACTIONS=("IGNORE","WAIT","SUGGEST","NOTIFY","ASK","ACT")

def _check(a:Sequence[str],b:Sequence[str])->None:
    if len(a)!=len(b): raise ValueError("label sequences must have equal length")
    if not a: raise ValueError("at least one paired label is required")

def raw_agreement(a:Sequence[str],b:Sequence[str])->float:
    _check(a,b); return sum(x==y for x,y in zip(a,b))/len(a)

def cohen_kappa(a:Sequence[str],b:Sequence[str])->float:
    _check(a,b); n=len(a); observed=raw_agreement(a,b); ca,cb=Counter(a),Counter(b); labels=set(ca)|set(cb); expected=sum((ca[label]/n)*(cb[label]/n) for label in labels)
    if expected==1.0: return 1.0 if observed==1.0 else 0.0
    return (observed-expected)/(1.0-expected)

def cohen_kappa_diagnostic(a:Sequence[str],b:Sequence[str])->tuple[float|None,str|None]:
    """Research-reporting form of kappa.

    Constant-class perfect agreement makes chance agreement exactly one. The
    legacy cohen_kappa function is preserved for compatibility, but formal
    Gate-B reporting must not present that degenerate case as ordinary kappa=1.
    """
    _check(a,b); n=len(a); observed=raw_agreement(a,b); ca,cb=Counter(a),Counter(b); labels=set(ca)|set(cb); expected=sum((ca[label]/n)*(cb[label]/n) for label in labels)
    if expected==1.0: return None,"DEGENERATE_EXPECTED_AGREEMENT_1_SINGLE_CLASS"
    return (observed-expected)/(1.0-expected),None

def confusion_matrix(a:Sequence[str],b:Sequence[str],labels:Sequence[str]=LEGAL_ACTIONS)->dict[str,dict[str,int]]:
    _check(a,b); matrix={x:{y:0 for y in labels} for x in labels}
    unknown=(set(a)|set(b))-set(labels)
    if unknown: raise ValueError(f"unknown labels for confusion matrix: {sorted(unknown)}")
    for x,y in zip(a,b): matrix[x][y]+=1
    return matrix

def per_class_agreement(a:Sequence[str],b:Sequence[str],labels:Sequence[str]=LEGAL_ACTIONS)->dict[str,float|None]:
    _check(a,b); out={}
    for label in labels:
        involved=[i for i,(x,y) in enumerate(zip(a,b)) if x==label or y==label]
        out[label]=None if not involved else sum(a[i]==label and b[i]==label for i in involved)/len(involved)
    return out
