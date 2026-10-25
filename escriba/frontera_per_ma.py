# Informació mútua de frontera (última lletra d'un mot | primera del següent, interior de línia) per mà de Davis, al text real
# i a l'escriba (5 llavors), amb i sense la regla de frontera. Mateixa definició que mesures.py (MI frontera k=1).
# Comparació amb Schwartz 2026 (0,12 i 0,21 bits a les mans 1 i 2). Ús (des de novetats/): PYTHONIOENCODING=utf-8 py -3 escriba/frontera_per_ma.py
import sys, os, random, numpy as np
ESC = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ESC); os.chdir(ESC)
import mesures as M
from escriba import Escriba, L_REAL

def mi_corr(L, seed=0):
    rng = random.Random(seed)
    r = M.MI(M.interior_pairs(L, 1, lambda w: w[-1], lambda w: w[0]))
    s = M.MI(M.interior_pairs(L, 1, lambda w: w[-1], lambda w: w[0], True, rng))
    return r, r - s

def by_hand(L, ref):
    out = {}
    for h in ('1', '2', 'tot'):
        sub = [l for l, rr in zip(L, ref) if h == 'tot' or rr['hand'] == h]
        out[h] = mi_corr(sub)
    return out

real = by_hand(L_REAL, L_REAL)
print('mà   real(brut)  real(corregit)  n_línies')
for h in ('1', '2', 'tot'):
    print(h, f'{real[h][0]:.3f}', f'{real[h][1]:.3f}', sum(1 for l in L_REAL if h == 'tot' or l['hand'] == h))
for name, kw in (('escriba', {}), ('sense frontera', {'use_boundary': False})):
    vals = {h: [] for h in ('1', '2', 'tot')}
    for s in (1, 2, 3, 4, 5):
        G = Escriba(**kw).write(seed=s)
        assert len(G) == len(L_REAL)
        r = by_hand(G, L_REAL)
        for h in vals: vals[h].append(r[h][1])
    print(name, {h: f'{np.mean(v):.3f}±{np.std(v):.3f}' for h, v in vals.items()})
