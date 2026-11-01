# Calibrates the drift along the line (R14.9, 01/11/2026) on the odd folios only: the scribe learns from the odd folios, and the four
# strengths (ld_bench, ld_e, ld_o, ld_d) are scaled until its first-half -> second-half differences on the odd folios match the real ones.
# Measure: words 3 to n-1 of lines of >= 6 words; first half against second half of that stretch (as in the confirmation, LINIA_PREREG).
#   py -3 calibrate_line_drift.py   -> prints the strengths per round
import os, sys
os.environ['SCRIBE_TRAIN'] = 'odd'
import numpy as np
from scribe import Escriba, L_ALL, folio_num
FEATS = [('ld_bench', lambda w: w[:2] in ('ch', 'sh')), ('ld_e', lambda w: 'e' in w), ('ld_o', lambda w: w[:1] == 'o'), ('ld_d', lambda w: w[:1] == 'd')]
SIGN = {'ld_bench': -1, 'ld_e': -1, 'ld_o': 1, 'ld_d': 1}


def deltas(L):
    a = np.zeros((2, 4)); n = np.zeros(2)
    for l in L:
        if folio_num(l['page']) % 2 != 1: continue
        ws = l['ws']; m = len(ws)
        if m < 6: continue
        for k in range(2, m - 1):
            h = int((k - 2) / (m - 4) > 0.5); n[h] += 1; a[h] += [f(ws[k]) for _, f in FEATS]
    p = a / n[:, None]; return p[1] - p[0]


real = deltas(L_ALL)
print('real (odd folios):', dict(zip([f for f, _ in FEATS], real.round(4))))
kw = {'use_line_drift': True, 'ld_bench': 0.8, 'ld_e': 0.8, 'ld_o': 0.8, 'ld_d': 1.5}
for rnd in range(4):
    d = np.mean([deltas(Escriba(**kw).write(seed=s)) for s in (1, 2, 3)], axis=0)
    print(f'round {rnd}:', {k: round(kw[k], 3) for k in SIGN}, 'scribe deltas', d.round(4))
    for j, (f, _) in enumerate(FEATS):
        if d[j] * SIGN[f] > 0.002: kw[f] *= float(np.clip(real[j] / d[j], 0.5, 2.0))
        else: kw[f] *= 2.0
print('final:', {k: round(kw[k], 2) for k in SIGN})
