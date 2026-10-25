# Prova de generalització: l'escriba aprèn només dels folis senars i escriu la maqueta dels folis parells;
# es compara amb els parells reals. Referència: els senars reals contra els parells reals (diferència natural entre meitats).
import os, sys, json, numpy as np
os.environ['ESCRIBA_TRAIN']='senars'
import mesures as M
from escriba import Escriba, L_ALL, folio_num
odd=[l for l in L_ALL if folio_num(l['page'])%2==1]; even=[l for l in L_ALL if folio_num(l['page'])%2==0]
print(f'senars: {len(odd)} línies; parells: {len(even)} línies')
R_even=M.evaluate(even,seed=1); R_odd=M.evaluate(odd,seed=1)
kw={}
for a in sys.argv[1:]:                     # clau=valor: l'escriba amb paràmetres canviats (com a compara.py)
    k,v=a.split('='); kw[k]=(v=='True') if v in ('True','False') else (float(v) if v.replace('.','',1).isdigit() else v)
rs=[M.evaluate(Escriba(**kw).write(seed=s,layout=even),seed=s) for s in (1,2,3,4,5)]
G={k:float(np.mean([r[k] for r in rs])) for k in rs[0]}
keys=list(R_even)
err=lambda c: np.nanmedian([abs(np.log(max(abs(c[k]),1e-6)/max(abs(R_even[k]),1e-6))) for k in keys if abs(R_even[k])>=0.02 and c[k]==c[k]])
okG=M.compare(R_even,G); okO=M.compare(R_even,R_odd)
print(f"{'mesura':62}{'parells reals':>14}{'senars reals':>14}{'escriba (après dels senars)':>30}")
for k in keys: print(f"{k[:62]:62}{R_even[k]:14.3f}{R_odd[k]:12.3f} {'✓' if okO[k] else '·'}{G[k]:28.3f} {'✓' if okG[k] else '·'}")
print(f"{'REPRODUÏDES (±25%)':62}{'':14}{sum(okO.values()):>12d}/{len(keys)}{sum(okG.values()):>26d}/{len(keys)}")
print(f"{'ERROR MEDIÀ':62}{'':14}{err(R_odd):>14.3f}{err(G):>28.3f}")
json.dump(dict(parells=R_even,senars=R_odd,escriba=G,kw=kw),open('resultats_holdout.json' if not kw else 'resultats_holdout_prova.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
