# Calibrates the 'e' habit (and then the 'dy' habit) of each section (scribe.py, use_ehabit): the offset that makes the share of words with e
# (-y/-dy block, R2.4) in each section of the scribe match the real one. Writes sec_e.json. Usage: PYTHONIOENCODING=utf-8 py -3 calibrate_section_e.py  (with SCRIBE_TRAIN=odd, writes sec_e_odd.json and sec_dy_odd.json for holdout.py)
import json, math, numpy as np
from collections import defaultdict
from scribe import Escriba, L_REAL, L_ALL, _SFX
sec={l['page']:l['section'] for l in L_ALL}
def shares(L):
    d=defaultdict(list)
    for l in L:
        for w in l['ws']: d[sec[l['page']]].append('e' in w)
    return {k:float(np.mean(v)) for k,v in d.items() if len(v)>=300}
lg=lambda p: math.log(p/(1-p))
real=shares(L_REAL); print('real:',{k:round(v,3) for k,v in real.items()})
cur={k:0.0 for k in real}
for it in range(6):
    G=Escriba(use_ehabit=True,sec_e=cur).write(seed=7); g=shares(G)
    print(f'iteration {it}:',{k:f'{g[k]:.3f}/{real[k]:.3f}' for k in real},flush=True)
    for k in real: cur[k]=float(np.clip(cur[k]+1.5*(lg(real[k])-lg(g[k])),-4,4))
json.dump(cur,open(f'sec_e{_SFX}.json','w',encoding='utf-8'),ensure_ascii=False,indent=1); print('sec_e:',{k:round(v,2) for k,v in cur.items()})
# second step: -dy or -y among the e-words ending in y (the 'dy' habit), with the 'e' habit already calibrated
def dyshare(L):
    d=defaultdict(list)
    for l in L:
        for w in l['ws']:
            if 'e' in w and w.endswith('y'): d[sec[l['page']]].append(w.endswith('dy'))
    return {k:float(np.mean(v)) for k,v in d.items() if len(v)>=200}
realdy=dyshare(L_REAL); print('real -dy:',{k:round(v,3) for k,v in realdy.items()})
dy={k:0.0 for k in realdy}
for it in range(6):
    G=Escriba(use_ehabit=True,sec_e=cur,use_sec_dy=True,sec_dy=dy).write(seed=7); g=dyshare(G)
    print(f'iteration {it}:',{k:f'{g[k]:.3f}/{realdy[k]:.3f}' for k in realdy},flush=True)
    for k in realdy: dy[k]=float(np.clip(dy[k]+1.5*(lg(realdy[k])-lg(g[k])),-4,4))
json.dump(dy,open(f'sec_dy{_SFX}.json','w',encoding='utf-8'),ensure_ascii=False,indent=1); print('sec_dy:',{k:round(v,2) for k,v in dy.items()})
