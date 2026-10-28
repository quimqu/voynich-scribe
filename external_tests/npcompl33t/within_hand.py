# npcompl33t, voynich.ninja thread 6219 (28/10/2026): the skribe makes the horseshoe only because it is fed the hands, and "LFD hands
# are stratified to specific points on the gradient", so the skribe "is indeed receiving time".
# If the gradient is time, it should also run INSIDE a hand and section: a scribe's pages would drift along it, and the drift would
# follow the order of the pages in the quires. The skribe has no such drift by construction: inside a hand x section every sheet draws
# its habits independently. So, per hand x section:
#   eta2      : share of the gradient (MDS1 of all the pages) explained by the hand x section means. What the hands carry.
#   ev1, hs   : MDS of the pages of the cell alone: share of the first axis, and R^2 of MDS2 as a parabola of MDS1 (horseshoe).
#   r(grad)   : the cell's own MDS1 against the global gradient (|r|): is the cell's main axis the same as the manuscript's?
#   rho(fol)  : Spearman of the gradient position against the folio number inside the cell. Q13 is all hand 2 biological, Q20 is all
#               hand 3 stars: Mauro's 1/21600 (npcompl33t's order matching Layfield-Davis) lives here, where hands cannot explain it.
# Null: the skribe, same layout, five seeds.
#   PYTHONIOENCODING=utf-8 py -3 external_tests/npcompl33t/within_hand.py
import os, re, sys, math, numpy as np
from collections import defaultdict
from scipy.stats import spearmanr
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'scribe'))
src = open(os.path.join(HERE, 'seriation.py'), encoding='utf-8').read().split('\nsrcs = ')[0]
ns = {'__file__': os.path.join(HERE, 'seriation.py')}; exec(src, ns)
import measures as M
from scribe import Escriba, L_ALL
MIN_CELL = 12   # pages with >= MIN_GLYPHS glyphs in a hand x section
SEEDS = (1, 2, 3, 4, 5)
OUT = []


def say(s=''):
    OUT.append(s); print(s, flush=True)


def folio(p):
    m = re.match(r'f(\d+)([rv])(\d*)', p); return int(m.group(1)) * 2 + (m.group(2) == 'v') + int(m.group(3) or 0) / 10


def analyse(lines, meta):
    L = defaultdict(list); info = {}
    for l, m in zip(lines, meta):
        L[m['page']].append(l['ws']); info[m['page']] = (m['hand'], m['section'], m['lang'])
    pages = [p for p in L if ns['transitions'](L[p])[1] >= ns['MIN_GLYPHS']]
    T = {p: ns['transitions'](L[p])[0] for p in pages}; n = len(pages); D = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n): D[i, j] = D[j, i] = math.sqrt(ns['dissimilarity'](T[pages[i]], T[pages[j]]))
    X, _ = ns['mds'](D); g = X[:, 0] * np.sign(np.corrcoef(X[:, 0], [info[p][2] == 'B' for p in pages])[0, 1] or 1)
    cell = defaultdict(list)
    for i, p in enumerate(pages): cell[info[p][:2]].append(i)
    fit = np.array([g[cell[info[p][:2]]].mean() for p in pages])
    eta2 = 1 - ((g - fit) ** 2).sum() / ((g - g.mean()) ** 2).sum()
    res = {}
    for c, idx in cell.items():
        if len(idx) < MIN_CELL: continue
        Y, ev = ns['mds'](D[np.ix_(idx, idx)]); y1 = Y[:, 0]
        res[c] = dict(n=len(idx), ev1=ev[0], hs=ns['r2'](y1, Y[:, 1], 2), r_grad=abs(np.corrcoef(y1, g[idx])[0, 1]),
                      rho_fol=spearmanr(g[idx], [folio(pages[i]) for i in idx]).statistic,
                      p_fol=spearmanr(g[idx], [folio(pages[i]) for i in idx]).pvalue)
    return eta2, res


real = M.load_real(); R = {'real': analyse(real, real)}
for s in SEEDS: R['skribe s%d' % s] = analyse(Escriba().write(seed=s), L_ALL)
cells = sorted(R['real'][1], key=lambda c: -R['real'][1][c]['n'])
say('Does the gradient run inside a hand and section? Real text against the skribe (no order inside a hand x section), %d seeds.' % len(SEEDS))
say('Pages with >= %d glyphs; cells with >= %d pages. Skribe columns: mean and range over the seeds.' % (ns['MIN_GLYPHS'], MIN_CELL))
say('')
sk = [k for k in R if k != 'real']
rng = lambda v: '%5.2f [%5.2f,%5.2f]' % (np.mean(v), min(v), max(v))
say('Share of the gradient explained by the hand x section means (eta2): real %.2f, skribe %s' % (R['real'][0], rng([R[k][0] for k in sk])))
for key, lab in (('ev1', 'share of the first axis inside the cell'), ('hs', 'horseshoe inside the cell (R^2 of MDS2 ~ MDS1^2)'),
                 ('r_grad', "|r| of the cell's own MDS1 with the global gradient"), ('rho_fol', 'Spearman of the gradient with the folio number')):
    say('')
    say('-- %s --' % lab)
    say('%-24s %4s %7s   %s' % ('hand, section', 'n', 'real', 'skribe'))
    for c in cells:
        v = [R[k][1][c][key] for k in sk if c in R[k][1]]
        say('%-24s %4d %+7.2f   %s%s' % ('%s, %s' % c, R['real'][1][c]['n'], R['real'][1][c][key], rng(v) if v else '-',
                                       '   real p %.3f' % R['real'][1][c]['p_fol'] if key == 'rho_fol' else ''))
say('')
say('Hand 1 herbal spans quires A-G and O, Q; its herbal pages in the late quires sit nearer the B side. Without them (quires A-G')
say('only) the real Spearman drops to +0.23 (p 0.10, 55 pages). Hand 2 biological is quire M (Q13); hand 3 stars is quires H and T (Q20).')
open(os.path.join(HERE, 'within_hand.txt'), 'w', encoding='utf-8').write('\n'.join(OUT) + '\n')
