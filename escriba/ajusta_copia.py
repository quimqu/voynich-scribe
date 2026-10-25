# Exploració dels paràmetres de còpia sobre les mesures de repetició (una llavor)
import json, itertools, numpy as np, mesures as M
from escriba import Escriba
Rr=json.load(open('mesures_real.json',encoding='utf-8'))
K=['AA / atzar','quasi(ed=1) / base','repetició k=2 / base','repetició k=5 / base','mots freq. amb rep >3x atzar (%)','mots freq. amb rep <0.3x (%)','tipus','hàpax (%)','[A1] mots amb bessó (ED≤1) abans a la pàgina (%)','[A1] línies fins al bessó més proper (mediana)','[G6] cosinus mateix full / pàgines veïnes d\'altres fulls']
print('real: '+'  '.join(f'{Rr[k]:.2f}' for k in K))
rows=[]
for rc,tau,rm in itertools.product([0.35,0.5,0.65],[1.5,4.0,10.0],[0.45,0.65]):
    R=M.evaluate(Escriba(r_copy=rc,tau=tau,r_mod=rm).write(seed=5),seed=5)
    err=np.mean([abs(np.log(max(R[k],1e-6)/max(Rr[k],1e-6))) for k in K]); ok=sum(M.compare({k:Rr[k] for k in K},R).values())
    rows.append((err,rc,tau,rm)); print(f'r_copy={rc} tau={tau} r_mod={rm}: ok {ok}/{len(K)} err {err:.3f} | '+'  '.join(f'{R[k]:.2f}' for k in K),flush=True)
print('millor:',min(rows))
