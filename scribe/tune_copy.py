# Exploration of the copying parameters on the repetition measures (one seed)
import json, itertools, numpy as np, measures as M
from scribe import Escriba
Rr=json.load(open('measures_real.json',encoding='utf-8'))
K=['Adjacent identical words / chance','Consecutive words at edit distance 1 / shuffled','Same word at distance 2 / shuffled','Same word at distance 5 / shuffled','Frequent words repeated >3x chance (%)','Frequent words repeated <0.3x chance (%)','Word types','Hapax (% of types)','[A1] Words with an edit-distance-1 twin earlier on the page (%)','[A1] Lines back to the nearest twin (median)','[G6] Vocabulary cosine: same sheet / neighbouring pages of other sheets']
print('real: '+'  '.join(f'{Rr[k]:.2f}' for k in K))
rows=[]
for rc,tau,rm in itertools.product([0.35,0.5,0.65],[1.5,4.0,10.0],[0.45,0.65]):
    R=M.evaluate(Escriba(r_copy=rc,tau=tau,r_mod=rm).write(seed=5),seed=5)
    err=np.mean([abs(np.log(max(R[k],1e-6)/max(Rr[k],1e-6))) for k in K]); ok=sum(M.compare({k:Rr[k] for k in K},R).values())
    rows.append((err,rc,tau,rm)); print(f'r_copy={rc} tau={tau} r_mod={rm}: ok {ok}/{len(K)} err {err:.3f} | '+'  '.join(f'{R[k]:.2f}' for k in K),flush=True)
print('best:',min(rows))
