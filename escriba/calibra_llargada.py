# Calibra els pesos de llargada dels mots nous per posició a la línia (primer, interior, últim) perquè la distribució de
# llargades de tot el text (còpies incloses) s'acosti a la real. Tres passades multiplicatives amorties. Escriu len_w.json
# (o len_w_senars.json amb ESCRIBA_TRAIN=senars, per a holdout.py). Ús (des de escriba/): py -3 calibra_llargada.py
import os, json, numpy as np
from collections import Counter
import mesures as M
from escriba import Escriba, L_REAL, _SFX
def pos(l, i): return 'first' if i == 0 else ('last' if i == len(l['ws']) - 1 else 'mid')
def dist(L):
    D = {k: Counter() for k in ('first', 'mid', 'last')}
    for l in L:
        for i, w in enumerate(l['ws']): D[pos(l, i)][str(min(len(M.gl(w)), 10))] += 1
    return {k: {x: v / sum(c.values()) for x, v in c.items()} for k, c in D.items()}
R = dist(L_REAL); W = {k: {str(x): 1.0 for x in range(1, 11)} for k in R}
for it in range(3):
    Gd = [dist(Escriba(len_w=W).write(seed=s, layout=L_REAL)) for s in (11, 12)]
    for k in W:
        for x in W[k]:
            g = np.mean([d[k].get(x, 0.0) for d in Gd]); r = R[k].get(x, 0.0)
            if g > 0 and r > 0: W[k][x] = float(np.clip(W[k][x] * (r / g) ** 0.7, 0.2, 5.0))
    err = np.mean([abs(np.mean([d[k].get(x, 0) for d in Gd]) - R[k].get(x, 0)) for k in W for x in W[k]])
    print(f'passada {it + 1}: error mitjà per classe {err:.4f}')
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'len_w{_SFX}.json')
json.dump(W, open(out, 'w', encoding='utf-8'), indent=1); print('desat', out)
