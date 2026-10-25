# Calibrates the repetition propensity of each word family (G7) by comparing the adjacent repetition per family in the real text and in the scribe
import json, numpy as np, measures as M
from collections import Counter, defaultdict
from scribe import Escriba, L_REAL, family, FAMREP
def fam_ratio(L):
    toks=[w for l in L for w in l['ws']]; N=len(toks); c=Counter(toks); cnt=Counter(); nx=Counter()
    for l in L:
        for a,b in zip(l['ws'],l['ws'][1:]): cnt[a]+=1; nx[a]+=(a==b)
    by=defaultdict(lambda:[0.0,0.0])
    for w in cnt:
        if cnt[w]>=40: by[family(w)][0]+=nx[w]; by[family(w)][1]+=cnt[w]*(c[w]/N)
    return {f:v[0]/v[1] for f,v in by.items() if v[1]>0}
real=fam_ratio(L_REAL); print('real:',{k:round(v,2) for k,v in real.items()})
fr=dict(FAMREP)
for it in range(4):
    G=Escriba(famrep=fr).write(seed=7); g=fam_ratio(G)
    print(f'iteration {it}: scribe',{k:round(v,2) for k,v in g.items()},'| famrep',{k:round(v,2) for k,v in fr.items()})
    for f in fr:
        if f in g and g[f]>0 and f in real: fr[f]=float(np.clip(fr[f]*(real[f]/g[f])**0.8,0.05,20))
json.dump(fr,open('famrep.json','w',encoding='utf-8'),ensure_ascii=False,indent=1); print('final:',{k:round(v,2) for k,v in fr.items()})
