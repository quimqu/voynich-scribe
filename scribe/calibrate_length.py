# Calibrates the length weights of new words by position in the line (first, interior, last) so that the length distribution
# of the whole text (copies included) gets close to the real one. Three damped multiplicative passes. Writes len_w.json
# (or len_w_odd.json with SCRIBE_TRAIN=odd, for holdout.py). Usage (from scribe/): py -3 calibrate_length.py
import os, json, numpy as np
from collections import Counter
import measures as M
from scribe import Escriba, L_REAL, _SFX
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
    print(f'pass {it + 1}: mean error per class {err:.4f}')
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'len_w{_SFX}.json')
json.dump(W, open(out, 'w', encoding='utf-8'), indent=1); print('saved', out)
