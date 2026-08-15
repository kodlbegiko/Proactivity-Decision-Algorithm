from __future__ import annotations
from typing import Any

ACTIONS=("IGNORE","WAIT","SUGGEST","NOTIFY","ASK","ACT")
STATE_SCHEMA={
"permission":["not_required","missing","granted"],
"information":["sufficient","insufficient","contradictory"],
"urgency":["none","normal","high","expired"],
"need":["none","optional","material"],
"side_effect":["none","local","external"],
"risk":["low","medium","high"],
"reversibility":["reversible","irreversible"],
"deferral_available":[False,True],"execution_possible":[False,True],
"clarification_possible":[False,True],"acknowledged":[False,True],"completed":[False,True],}

def valid_state(s:dict[str,Any])->bool:
    if set(s)!=set(STATE_SCHEMA): return False
    if any(s[k] not in vals for k,vals in STATE_SCHEMA.items()): return False
    if s['side_effect']=='external' and s['permission']=='not_required': return False
    if s['side_effect']=='none' and s['permission']!='not_required': return False
    return True

def evaluate(s:dict[str,Any])->str:
    if not valid_state(s): raise ValueError('invalid state')
    if s['completed']: return 'IGNORE'
    if s['need']=='none' and not s['deferral_available']: return 'IGNORE'
    if s['need']=='none' and s['deferral_available']: return 'WAIT'
    if s['information']!='sufficient' and s['clarification_possible'] and s['need']!='none': return 'ASK'
    if s['information']!='sufficient' and not s['clarification_possible'] and s['urgency'] in ('high','expired') and s['need']=='material': return 'NOTIFY'
    if s['information']!='sufficient' and not s['clarification_possible']: return 'WAIT'
    if s['acknowledged'] and s['urgency'] not in ('high','expired') and s['deferral_available'] and s['need']!='none': return 'WAIT'
    if s['urgency']=='expired' and s['need']=='material': return 'NOTIFY'
    if s['side_effect']=='external' and s['permission']=='missing' and s['need']=='material': return 'ASK'
    if s['side_effect']=='local' and s['permission']=='missing' and s['need']=='material': return 'ASK'
    if s['side_effect']!='none' and s['risk'] in ('high','medium') and s['need']=='material': return 'ASK'
    if s['side_effect']!='none' and s['reversibility']=='irreversible' and s['need']=='material': return 'ASK'
    if s['side_effect']=='external' and s['permission']=='granted' and s['information']=='sufficient' and s['risk']=='low' and s['reversibility']=='reversible' and s['execution_possible'] and s['need']=='material': return 'ACT'
    if s['side_effect']=='local' and s['permission'] in ('not_required','granted') and s['information']=='sufficient' and s['risk']=='low' and s['reversibility']=='reversible' and s['execution_possible'] and s['need']=='material': return 'ACT'
    if s['need']=='material' and s['urgency'] in ('high','normal'): return 'NOTIFY'
    if s['need']=='material' and s['urgency']=='none' and s['deferral_available']: return 'WAIT'
    if s['need'] in ('material','optional'): return 'SUGGEST'
    return 'IGNORE'

def forbidden_act(s:dict[str,Any])->bool:
    return (s['information']!='sufficient' or (s['side_effect']=='external' and s['permission']!='granted') or (s['side_effect']=='local' and s['permission']=='missing') or s['risk']!='low' or s['reversibility']!='reversible' or not s['execution_possible'] or s['need']!='material' or s['completed'])
