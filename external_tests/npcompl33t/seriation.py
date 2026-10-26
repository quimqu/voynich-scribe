# npcompl33t's page seriation (voynich.ninja threads 6182, 6215, 6223, October 2026), rebuilt from his descriptions and run on the
# real text and on the skribe. Per page: glyph transition counts within words (with word start and end) and along the line with the
# spaces removed, added together. Between two pages: for each starting glyph g with at least 3 outgoing transitions on both pages,
# the Jensen-Shannon divergence of P(h|g); weighted by the share of g on the two pages; excluded rows are not redistributed. Classical
# MDS on the square root of that dissimilarity. A Guttman horseshoe shows as MDS2 ~ quadratic in MDS1 and MDS3 ~ S or W in MDS1.
# Also his "bifolio agreement": how close the pages of the same sheet are on MDS1.
# Differences from his pipeline we cannot avoid: paragraph text only (ZL3b, as the skribe writes it), our glyph units (ch, sh, cth,
# ckh, cph, cfh as single glyphs), pages with at least MIN_GLYPHS glyphs; no curve fitting (ElPiGraph), only the MDS shapes.
#   PYTHONIOENCODING=utf-8 py -3 external_tests/npcompl33t/seriation.py
# Input: scribe/manuscript_out/{real,scribe_seed*}.txt. Output: here, seriation.{txt,png}
import os, re, glob, math
import numpy as np
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
MIN_GLYPHS, MIN_ROW = 300, 3
UNITS = re.compile(r'cth|ckh|cph|cfh|ch|sh|.')
OUT = []


def say(s=''):
    OUT.append(s); print(s, flush=True)


def read(path):
    P = {}; cur = None
    for ln in open(path, encoding='utf-8'):
        if ln.startswith('#') or not ln.strip():
            continue
        m = re.match(r'^<(f\d+[rv]\d*)>\s+<!(.*)>', ln)
        if m:
            cur = m.group(1); P[cur] = dict(dict(re.findall(r'\$(\w)=(\S+)', m.group(2))), lines=[]); continue
        m = re.match(r'^<[^>]+>\s*(.*)$', ln.rstrip('\n'))
        if not m or cur is None:
            continue
        ws = [w for w in m.group(1).replace('<%>', '').replace('<$>', '').replace('<->', '.').split('.') if w]
        if ws:
            P[cur]['lines'].append(ws)
    return P


def transitions(lines):
    T = defaultdict(Counter); n = 0
    for ws in lines:
        for w in ws:
            g = ['^'] + UNITS.findall(w) + ['$']
            for a, b in zip(g, g[1:]):
                T[a][b] += 1
        flat = [u for w in ws for u in UNITS.findall(w)]
        n += len(flat)
        for a, b in zip(flat, flat[1:]):
            T[a][b] += 1
    return T, n


def jsd(p, q):
    keys = set(p) | set(q); tp = sum(p.values()); tq = sum(q.values()); d = 0.0
    for k in keys:
        a = p.get(k, 0) / tp; b = q.get(k, 0) / tq; m = (a + b) / 2
        if a > 0: d += 0.5 * a * math.log2(a / m)
        if b > 0: d += 0.5 * b * math.log2(b / m)
    return d


def dissimilarity(Tp, Tq):
    np_ = sum(sum(c.values()) for c in Tp.values()); nq = sum(sum(c.values()) for c in Tq.values()); d = 0.0
    for g in set(Tp) | set(Tq):
        cp, cq = Tp.get(g, Counter()), Tq.get(g, Counter())
        w = 0.5 * (sum(cp.values()) / np_ + sum(cq.values()) / nq)
        if sum(cp.values()) >= MIN_ROW and sum(cq.values()) >= MIN_ROW:
            d += w * jsd(cp, cq)
    return d


def mds(D, k=3):
    n = len(D); J = np.eye(n) - 1 / n; B = -0.5 * J @ (D ** 2) @ J
    vals, vecs = np.linalg.eigh(B); idx = np.argsort(vals)[::-1]; vals, vecs = vals[idx], vecs[:, idx]
    X = vecs[:, :k] * np.sqrt(np.maximum(vals[:k], 0))
    return X, vals[:k] / vals[vals > 0].sum()


def r2(x, y, deg):
    c = np.polyfit(x, y, deg); res = y - np.polyval(c, x); return 1 - res.var() / y.var()


def analyse(path):
    P = read(path); pages = []; T = {}
    for pg, d in P.items():
        t, n = transitions(d['lines'])
        if n >= MIN_GLYPHS:
            pages.append(pg); T[pg] = t
    n = len(pages); D = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            D[i, j] = D[j, i] = math.sqrt(dissimilarity(T[pages[i]], T[pages[j]]))
    X, ev = mds(D)
    X[:, 0] *= np.sign(np.corrcoef(X[:, 0], [P[p]['L'] == 'B' for p in pages])[0, 1] or 1)   # same orientation for every text: B to the right
    secs = np.array([P[p]['S'] for p in pages])
    for k, (sname, sign) in ((1, ('pharmaceutical', 1)), (2, ('biological', -1))):   # MDS signs are arbitrary: fix them so every text plots the same way
        if np.sign(X[secs == sname, k].mean()) != sign: X[:, k] *= -1
    order = sorted({p['S'] for p in P.values() if p.get('S')} & set(secs), key=lambda s_: X[secs == s_, 0].mean())
    x = X[:, 0]; rng_ = x.max() - x.min()
    sheet = defaultdict(list)
    for i, p in enumerate(pages):
        sheet[P[p]['F']].append(i)
    same = [abs(x[a] - x[b]) / rng_ for idx in sheet.values() for k, a in enumerate(idx) for b in idx[k + 1:]]
    sec = defaultdict(list)
    for i, p in enumerate(pages):
        sec[P[p]['S']].append(i)
    same_sec = [abs(x[a] - x[b]) / rng_ for idx in sec.values() for k, a in enumerate(idx) for b in idx[k + 1:]]
    allp = [abs(x[a] - x[b]) / rng_ for a in range(n) for b in range(a + 1, n)]
    return dict(P=P, pages=pages, X=X, ev=ev, h2=r2(x, X[:, 1], 2), s3=r2(x, X[:, 2], 3), w3=r2(x, X[:, 2], 4),
                bif=float(np.mean(same)), order=' < '.join(order), bif_n=len(same), sec_=float(np.mean(same_sec)), allp=float(np.mean(allp)))


srcs = [('real', os.path.join(ROOT, 'scribe', 'manuscript_out', 'real.txt'))] + \
       [(os.path.basename(p)[:-4], p) for p in sorted(glob.glob(os.path.join(ROOT, 'scribe', 'manuscript_out', 'scribe_seed*.txt')))]
R = {s: analyse(p) for s, p in srcs}
say(f"npcompl33t's seriation, rebuilt. Pages with >= {MIN_GLYPHS} glyphs; weighted JS of P(next glyph | glyph), rows with >= {MIN_ROW} transitions on both pages; classical MDS.")
say('Horseshoe: R^2 of MDS2 as a parabola of MDS1. S / W: R^2 of MDS3 as a cubic / quartic of MDS1. Bifolio agreement: mean |MDS1 difference| as a share of the MDS1 range.')
say('')
say(f"{'text':14} {'pages':>5} {'var MDS1/2/3':>16} {'horseshoe R2':>12} {'S (cubic)':>9} {'W (quartic)':>11} {'same sheet':>10} {'same section':>12} {'any two pages':>13}")
for s, r in R.items():
    say(f"{s:14} {len(r['pages']):5d} {'/'.join(f'{v:.2f}' for v in r['ev']):>16} {r['h2']:12.2f} {r['s3']:9.2f} {r['w3']:11.2f} {100*r['bif']:9.1f}% {100*r['sec_']:11.1f}% {100*r['allp']:12.1f}%")
say('')
say('Order of the sections along MDS1 (mean of their pages):')
for s, r in R.items():
    say(f"  {s:14} {r['order']}")
say('')
say('Within a section (and hand), does the position on MDS1 follow the folio number? Spearman rho (p) per group with >= 12 pages.')
from scipy.stats import spearmanr
groups = [('herbal', '1'), ('herbal', '2'), ('stars', '3'), ('biological', '2'), ('pharmaceutical', '1')]
say('text           ' + ' | '.join(f'{g[0]} hand {g[1]}' for g in groups))
for s, r in R.items():
    cells = []
    for sec_, hand in groups:
        idx = [i for i, p in enumerate(r['pages']) if r['P'][p]['S'] == sec_ and r['P'][p]['H'] == hand]
        if len(idx) < 12:
            cells.append('n<12'); continue
        rho = spearmanr([int(re.match(r'f(\d+)', r['pages'][i]).group(1)) for i in idx], [r['X'][i, 0] for i in idx])
        cells.append(f'{rho.statistic:+.2f} ({rho.pvalue:.3f}, n {len(idx)})')
    say(f'{s:14} ' + ' | '.join(cells))
open(os.path.join(HERE, 'seriation.txt'), 'w', encoding='utf-8').write('\n'.join(OUT) + '\n')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
COL = {'herbal': '#2e7d32', 'biological': '#c62828', 'stars': '#1565c0', 'pharmaceutical': '#ef6c00', 'cosmological': '#6a1b9a', 'astro': '#8d6e63', 'text_only': '#757575'}
show = ['real', 'scribe_seed1', 'scribe_seed2']
fig, ax = plt.subplots(2, 3, figsize=(15, 9))
for c, s in enumerate(show):
    r = R[s]; X = r['X']; cols = [COL.get(r['P'][p]['S'], 'k') for p in r['pages']]; mk = ['o' if r['P'][p]['L'] == 'A' else '^' for p in r['pages']]
    for k, (yy, lab) in enumerate(((1, 'MDS2'), (2, 'MDS3'))):
        for xi, yi, ci, mi in zip(X[:, 0], X[:, yy], cols, mk):
            ax[k, c].scatter(xi, yi, c=ci, marker=mi, s=22, alpha=.8)
        ax[k, c].set_xlabel('MDS1'); ax[k, c].set_ylabel(lab)
    ax[0, c].set_title(('Real text (ZL3b)' if s == 'real' else f'Skribe, {s.replace("scribe_", "")}') + f"\nhorseshoe R² {r['h2']:.2f}, same sheet {100*r['bif']:.1f}% of MDS1")
for nm, cl in COL.items():
    ax[0, 0].scatter([], [], c=cl, label=nm)
ax[0, 0].scatter([], [], c='k', marker='o', label='Currier A'); ax[0, 0].scatter([], [], c='k', marker='^', label='Currier B')
ax[0, 0].legend(fontsize=8, loc='best')
fig.suptitle("npcompl33t's seriation (glyph transitions, Jensen-Shannon, MDS): real text and the skribe")
fig.tight_layout(); fig.savefig(os.path.join(HERE, 'seriation.png'), dpi=110)
