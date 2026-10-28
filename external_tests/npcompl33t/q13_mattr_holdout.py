# npcompl33t, voynich.ninja thread 6244 (28/10/2026): the skribe makes Q13 the poorest quire in MATTR only because "it was trained on
# the very data you are having it predict". Two ways to keep the skribe from seeing the pages it writes:
#   odd       : it learns from the odd folios only and writes the even ones (Q13: f76, f78, f80, f82, f84); compared with the real even folios.
#   without_M : it learns from everything except Q13 and writes the whole layout; Q13 then falls back on hand 2's habits in other sections.
# MATTR as in the thread: per folio, mean share of different words in windows of 100 words; then the mean per quire (>= 3 folios).
#   PYTHONIOENCODING=utf-8 py -3 external_tests/npcompl33t/q13_mattr_holdout.py      (both modes, ~1 min; writes q13_mattr_holdout.txt)
import os, re, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
if len(sys.argv) < 2:   # SCRIBE_TRAIN is read when scribe.py is imported, so each mode runs in its own process
    out = [subprocess.run([sys.executable, __file__, m], capture_output=True, text=True, encoding='utf-8', check=True,
                          env=dict(os.environ, PYTHONIOENCODING='utf-8')).stdout for m in ('odd', 'without_M')]
    print('\n'.join(out), end=''); open(os.path.join(HERE, 'q13_mattr_holdout.txt'), 'w', encoding='utf-8').write('\n'.join(out))
    sys.exit()
import numpy as np
from collections import defaultdict
mode = sys.argv[1]; os.environ['SCRIBE_TRAIN'] = mode
sys.path.insert(0, os.path.join(ROOT, 'scribe'))
import measures as M
from scribe import Escriba, L_ALL, folio_num
SEEDS = (1, 2, 3, 4, 5)


def folio(pg): return re.sub(r'[rv]\d*$', '', pg)


def mattr(ws, w=100):
    return float(np.mean([len(set(ws[i:i + w])) / w for i in range(0, len(ws) - w + 1)])) if len(ws) >= w + 50 else np.nan


def quires(lines, meta):
    F = defaultdict(list); q = {}
    for l, m in zip(lines, meta): F[folio(m['page'])] += l['ws']; q[folio(m['page'])] = m['quire']
    g = defaultdict(list)
    for f, ws in F.items():
        v = mattr(ws)
        if v == v: g[q[f]].append(v)
    return {k: np.mean(v) for k, v in g.items() if len(v) >= 3}


def report(lab, Qs):
    m = {k: np.mean([Q[k] for Q in Qs]) for k in Qs[0] if all(k in Q for Q in Qs)}
    others = np.mean([v for k, v in m.items() if k != 'M'])
    rank = sorted(m, key=m.get).index('M') + 1
    print('%-36s Q13 %.3f | other quires %.3f | Q13 rank %d/%d (1 = poorest)' % (lab, m['M'], others, rank, len(m)))


real = M.load_real()
lay = [l for l in L_ALL if folio_num(l['page']) % 2 == 0] if mode == 'odd' else L_ALL
rl = [l for l in real if folio_num(l['page']) % 2 == 0] if mode == 'odd' else real
print('## %s: %s' % (mode, 'learned from the odd folios, even folios written' if mode == 'odd' else 'learned without Q13, all folios written'))
report('real text', [quires(rl, rl)])
for lab, kw in (('skribe', {}), ('skribe, no copying', {'use_copy': False})):
    report('%s (%d seeds)' % (lab, len(SEEDS)), [quires(Escriba(**kw).write(seed=s, layout=lay), lay) for s in SEEDS])
