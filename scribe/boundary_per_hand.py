# Boundary mutual information (last letter of a word | first letter of the next, line interior) per Davis hand, in the real text
# and in the scribe (5 seeds), with and without the boundary rule. Same definition as measures.py (Boundary MI, distance 1 (last glyph to next first glyph)).
# Comparison with Schwartz 2026 (0.12 and 0.21 bits in hands 1 and 2). Usage (from the repository root): PYTHONIOENCODING=utf-8 py -3 scribe/boundary_per_hand.py
import sys, os, random, numpy as np
ESC = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ESC); os.chdir(ESC)
import measures as M
from scribe import Escriba, L_REAL

def mi_corr(L, seed=0):
    rng = random.Random(seed)
    r = M.MI(M.interior_pairs(L, 1, lambda w: w[-1], lambda w: w[0]))
    s = M.MI(M.interior_pairs(L, 1, lambda w: w[-1], lambda w: w[0], True, rng))
    return r, r - s

def by_hand(L, ref):
    out = {}
    for h in ('1', '2', 'all'):
        sub = [l for l, rr in zip(L, ref) if h == 'all' or rr['hand'] == h]
        out[h] = mi_corr(sub)
    return out

real = by_hand(L_REAL, L_REAL)
print('hand   real(raw)  real(corrected)  n_lines')
for h in ('1', '2', 'all'):
    print(h, f'{real[h][0]:.3f}', f'{real[h][1]:.3f}', sum(1 for l in L_REAL if h == 'all' or l['hand'] == h))
for name, kw in (('scribe', {}), ('without boundary', {'use_boundary': False})):
    vals = {h: [] for h in ('1', '2', 'all')}
    for s in (1, 2, 3, 4, 5):
        G = Escriba(**kw).write(seed=s)
        assert len(G) == len(L_REAL)
        r = by_hand(G, L_REAL)
        for h in vals: vals[h].append(r[h][1])
    print(name, {h: f'{np.mean(v):.3f}±{np.std(v):.3f}' for h, v in vals.items()})
