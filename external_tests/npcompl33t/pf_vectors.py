# npcompl33t, voynich.ninja thread 6231: "P/F words lag K/T words along the chronological gradient".
# His method, rebuilt: per sheet (bifolio), pool the gallows words whose gallows are p/f and those whose gallows are k/t, write every
# gallows as G, and place both pools in one MDS of glyph transitions. The gradient is MDS1 of all the words of each sheet (B to the right).
# For each sheet, the arrow PF -> KT is compared with the direction in which the pools move along the gradient.
# Question: does the skribe, which has no chronology, show the same lag? With the old random k->p swap and with the no-e rule (27/10).
# Usage (from the repo root): py -3 external_tests/npcompl33t/pf_vectors.py
import os, re, sys, math, numpy as np
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'scribe'))
src = open(os.path.join(HERE, 'seriation.py'), encoding='utf-8').read().split('\nsrcs = ')[0]
ns = {'__file__': os.path.join(HERE, 'seriation.py')}; exec(src, ns)
import measures as M
from scribe import Escriba, L_ALL
UNITS = ns['UNITS']; MIN_POOL = 120   # glyphs in a sheet's p/f pool (p/f words are few: ~1,100 in the whole text)
GALL = {'k', 't', 'p', 'f', 'ckh', 'cth', 'cph', 'cfh'}
def gword(w): return ''.join('G' if u in GALL else u for u in UNITS.findall(w))
def kind(w):
    u = set(UNITS.findall(w)) & GALL
    if not u: return None
    pf = bool(u & {'p', 'f', 'cph', 'cfh'}); kt = bool(u & {'k', 't', 'ckh', 'cth'})
    return 'PF' if pf and not kt else 'KT' if kt and not pf else None
def analyse(lines, meta, mode='pf'):
    # mode 'pf': p/f words against k/t words (npcompl33t). 'head': the same, but both pools from paragraph head lines only.
    # 'pos': no p/f at all, k/t words of head lines (in the PF slot) against k/t words of the other lines.
    ALL = defaultdict(list); POOL = defaultdict(list); lang = {}
    for l, m in zip(lines, meta):
        s = m['sheet']; ALL[s].append(l['ws']); lang[s] = m['lang']
        for i, w in enumerate(l['ws']):
            k = kind(w); head = m['ps'] == 1 and i > 0
            if mode == 'head' and not head: k = None
            if mode == 'pos': k = None if k != 'KT' else 'PF' if head else 'KT'
            if k: POOL[(s, k)].append([gword(w)])
    # gradient: MDS1 of all the words of each sheet
    sh = [s for s in ALL if ns['transitions'](ALL[s])[1] >= ns['MIN_GLYPHS']]
    T = {s: ns['transitions'](ALL[s])[0] for s in sh}; n = len(sh); D = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n): D[i, j] = D[j, i] = math.sqrt(ns['dissimilarity'](T[sh[i]], T[sh[j]]))
    X, _ = ns['mds'](D); g = X[:, 0] * np.sign(np.corrcoef(X[:, 0], [lang[s] == 'B' for s in sh])[0, 1] or 1)
    grad = dict(zip(sh, (g - g.min()) / (g.max() - g.min())))
    # pools: one MDS for every PF and KT point
    use = [s for s in sh if ns['transitions'](POOL[(s, 'PF')])[1] >= MIN_POOL]
    pts = [(s, k) for s in use for k in ('PF', 'KT')]; TP = {p: ns['transitions'](POOL[p])[0] for p in pts}; m_ = len(pts); D = np.zeros((m_, m_))
    for i in range(m_):
        for j in range(i + 1, m_): D[i, j] = D[j, i] = math.sqrt(ns['dissimilarity'](TP[pts[i]], TP[pts[j]]))
    Y, _ = ns['mds'](D, 2); idx = {p: i for i, p in enumerate(pts)}
    gx = np.array([grad[s] for s, _ in pts])
    v = np.array([np.polyfit(gx, Y[:, c], 1)[0] for c in (0, 1)]); v /= np.linalg.norm(v)   # where the pools move as the gradient advances
    cos, gap, gpos = [], [], []
    for s in use:
        a = Y[idx[(s, 'KT')]] - Y[idx[(s, 'PF')]]
        cos.append(float(a @ v / np.linalg.norm(a))); gap.append(D[idx[(s, 'PF')], idx[(s, 'KT')]]); gpos.append(grad[s])
    cos, gap, gpos = map(np.array, (cos, gap, gpos))
    return dict(n=len(use), cos=cos.mean(), ahead=(cos > 0).mean(), r_gap=np.corrcoef(gpos, gap)[0, 1], gap=gap.mean())
def show(lab, r): print('%-38s %4d %9.2f %9.0f%% %10.2f %+11.2f' % (lab, r['n'], r['cos'], 100 * r['ahead'], r['gap'], r['r_gap']))
if __name__ == '__main__':
    print('Arrow PF -> KT per sheet against the direction of the gradient (sheets with >= %d glyphs of p/f words)' % MIN_POOL)
    print('%-38s %4s %9s %10s %10s %11s' % ('text', 'n', 'mean cos', 'KT ahead', 'gap PF-KT', 'r(gap,grad)'))
    real = M.load_real()
    G = {(lab, s): Escriba(**kw).write(seed=s) for lab, kw in (('skribe, no-e rule (27/10)', {}), ('skribe, random k->p swap', {'use_pf_noe': False}),
                                                                 ('skribe, random swap, no 1st-line style', {'use_pf_noe': False, 'use_fl_style': False})) for s in (1, 2, 3)}
    for mode, title in (('pf', 'p/f words against k/t words'), ('head', 'the same, both pools from head lines only'),
                        ('pos', 'control without p/f: k/t words of head lines against k/t words of other lines')):
        print('\n-- %s --' % title)
        show('real', analyse(real, real, mode))
        for (lab, s), g in G.items(): show('%s s%d' % (lab[:34], s), analyse(g, L_ALL, mode))
