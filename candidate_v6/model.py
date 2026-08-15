from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline, FeatureUnion
from candidate_v6.policy import STATE_SCHEMA, evaluate, valid_state

ACT_CRITICAL={'permission','information','need','side_effect','risk','reversibility','execution_possible'}
SAFE_DEFAULT={'permission':'missing','information':'insufficient','urgency':'none','need':'optional','side_effect':'local','risk':'high','reversibility':'irreversible','deferral_available':True,'execution_possible':False,'clarification_possible':True,'acknowledged':False,'completed':False}

@dataclass
class Prediction:
    action:str
    state:dict
    evidence:dict

class FactorModel:
    """Factor reconstruction model. No direct action-class head is used."""
    def __init__(self, variant='V6-B', unknown_threshold=0.50):
        self.variant=variant; self.unknown_threshold=unknown_threshold; self.models={}

    def _vectorizer(self):
        if self.variant=='V6-B':
            return TfidfVectorizer(ngram_range=(1,2),min_df=2,max_features=18000,lowercase=True)
        if self.variant=='V6-C':
            return TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),min_df=2,max_features=30000,lowercase=True)
        return FeatureUnion([
            ('w',TfidfVectorizer(ngram_range=(1,2),min_df=2,max_features=18000,lowercase=True)),
            ('c',TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),min_df=2,max_features=30000,lowercase=True))])

    def fit(self,rows):
        X=[r['observation'] for r in rows]
        for f in STATE_SCHEMA:
            y=[str(r['state'][f]) for r in rows]
            pipe=Pipeline([('vec',self._vectorizer()),('clf',LogisticRegression(max_iter=500,C=4.0,class_weight='balanced',random_state=17))])
            pipe.fit(X,y); self.models[f]=pipe
        return self

    def predict_texts(self,texts):
        raw_by_field={}; conf_by_field={}
        for f,pipe in self.models.items():
            probs=pipe.predict_proba(texts); classes=pipe.classes_; inds=np.argmax(probs,axis=1)
            raw_by_field[f]=[classes[i] for i in inds]
            conf_by_field[f]=[probs[j,i] for j,i in enumerate(inds)]
        out=[]
        for idx in range(len(texts)):
            state={}; evidence={}; unknown_critical=False
            for f in STATE_SCHEMA:
                raw=raw_by_field[f][idx]; conf=float(conf_by_field[f][idx])
                val=True if raw=='True' else False if raw=='False' else raw
                status='SUPPORTED' if conf>=self.unknown_threshold else 'INSUFFICIENT_EVIDENCE'
                evidence[f]={'factor':f,'value':val if status=='SUPPORTED' else 'UNKNOWN','status':status,'supporting_spans':[],'contradicting_spans':[],'confidence':conf,'source_sentence_ids':[]}
                if status!='SUPPORTED' and f in ACT_CRITICAL: unknown_critical=True
                state[f]=val if status=='SUPPORTED' else SAFE_DEFAULT[f]
            if self.variant=='V6-D':
                if state['side_effect']=='none': state['permission']='not_required'
                elif state['side_effect']=='external' and state['permission']=='not_required': state['permission']='missing'
            if not valid_state(state): state=dict(SAFE_DEFAULT)
            action=evaluate(state)
            if unknown_critical and action=='ACT': action='ASK'
            out.append(Prediction(action,state,evidence))
        return out

    def predict(self,rows):
        return self.predict_texts([r['observation'] for r in rows])
