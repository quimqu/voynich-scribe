# Generalisation test: the scribe learns only from the odd folios and writes the layout of the even folios;
# it is compared with the real even folios. Reference: the real odd folios against the real even ones (natural difference between halves).
import os, sys, json, numpy as np
os.environ['SCRIBE_TRAIN']='odd'
import measures as M
from scribe import Escriba, L_ALL, folio_num
odd=[l for l in L_ALL if folio_num(l['page'])%2==1]; even=[l for l in L_ALL if folio_num(l['page'])%2==0]
print(f'odd: {len(odd)} lines; even: {len(even)} lines')
R_even=M.evaluate(even,seed=1); R_odd=M.evaluate(odd,seed=1)
kw={}
for a in sys.argv[1:]:                     # key=value: the scribe with changed parameters (as in compare.py)
    k,v=a.split('='); kw[k]=(v=='True') if v in ('True','False') else (float(v) if v.replace('.','',1).isdigit() else v)
rs=[M.evaluate(Escriba(**kw).write(seed=s,layout=even),seed=s) for s in (1,2,3,4,5)]
G={k:float(np.mean([r[k] for r in rs])) for k in rs[0]}
keys=list(R_even)
err=lambda c: np.nanmedian([abs(np.log(max(abs(c[k]),1e-6)/max(abs(R_even[k]),1e-6))) for k in keys if abs(R_even[k])>=0.02 and c[k]==c[k]])
okG=M.compare(R_even,G); okO=M.compare(R_even,R_odd)
print(f"{'measure':62}{'real even':>14}{'real odd':>14}{'scribe (learned from odd)':>30}")
for k in keys: print(f"{k[:62]:62}{R_even[k]:14.3f}{R_odd[k]:12.3f} {'✓' if okO[k] else '·'}{G[k]:28.3f} {'✓' if okG[k] else '·'}")
print(f"{'REPRODUCED (±25%)':62}{'':14}{sum(okO.values()):>12d}/{len(keys)}{sum(okG.values()):>26d}/{len(keys)}")
print(f"{'MEDIAN ERROR':62}{'':14}{err(R_odd):>14.3f}{err(G):>28.3f}")
json.dump(dict(even=R_even,odd=R_odd,scribe=G,kw=kw),open('results_holdout.json' if not kw else 'results_holdout_trial.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
