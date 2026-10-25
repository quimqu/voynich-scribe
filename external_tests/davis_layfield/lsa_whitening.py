# What the Davis-Layfield LSA measures (pre-registered in WHITENING_PREREG.md). Folding v = q U_k / S_k and the cosine amount to a
# whitened similarity q_x (A^T A)^+ q_y: the large directions of variation (styles of hand and section) are divided out. Primary
# measure DEV, transparent and without SVD: how each page deviates from its hand's usual vocabulary (z-scores of word frequencies
# against the other pages of the same hand), compared by cosine. Secondary: DEV against hand x section; full-rank ridge-whitened
# similarity; plain cosine after removing the top principal directions; LSA for reference.
#   PYTHONIOENCODING=utf-8 py -3 external_tests/davis_layfield/lsa_whitening.py
# Input: scribe/manuscript_out/{real,scribe_seed*}.txt. Output: here, lsa_whitening.{txt,json}
import os, glob, json, math
import numpy as np
from collections import Counter
from scipy.stats import wilcoxon
HERE = os.path.dirname(os.path.abspath(__file__))
ns = {'__file__': os.path.join(HERE, 'sheet_order.py')}
exec(open(os.path.join(HERE, 'sheet_order.py'), encoding='utf-8').read().split('srcs = ')[0], ns)
read, bifolia, PAIRS, NOV = ns['read'], ns['bifolia'], ns['PAIRS'], ns['NOV']
CHUNK, MINREM, K, MINPAGES = 40, 20, 75, 5
OUT = []


def say(s=''):
    OUT.append(s); print(s, flush=True)


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb)) if na > 0 and nb > 0 else 0.0


class Space:
    def __init__(self, P):
        self.pages = {pg: [w for l in d['lines'] for w in l] for pg, d in P.items()}
        docs = [ws[i:i + CHUNK] for ws in self.pages.values() for i in range(0, len(ws), CHUNK) if len(ws[i:i + CHUNK]) >= MINREM]
        df = Counter()
        for c in docs:
            df.update(set(c))
        terms = sorted(t for t in df if df[t] >= 2); self.ix = {t: i for i, t in enumerate(terms)}
        self.idf = np.array([math.log(len(docs) / df[t]) for t in terms])
        A = np.array([self.tfidf(c) for c in docs])
        _, self.S, Vt = np.linalg.svd(A, full_matrices=False); self.V = Vt.T          # A^T A = V S^2 V^T
        self.q = {pg: self.tfidf(ws) for pg, ws in self.pages.items()}

    def tfidf(self, ws):
        q = np.zeros(len(self.ix))
        for w, n in Counter(ws).items():
            if w in self.ix:
                q[self.ix[w]] = n
        return q * self.idf

    def lsa(self, x, y):
        f = lambda q: (q @ self.V[:, :K]) / self.S[:K]
        return cos(f(self.q[x]), f(self.q[y]))

    def ridge(self, x, y, lam):
        """q_x (A^T A + lam I)^-1 q_y, normalised; the part of q outside the span of V gets weight 1/lam"""
        def inner(a, b):
            pa, pb = a @ self.V, b @ self.V
            return float(np.sum(pa * pb / (self.S ** 2 + lam)) + (a @ b - pa @ pb) / lam)
        a, b = self.q[x], self.q[y]; d = math.sqrt(inner(a, a) * inner(b, b))
        return inner(a, b) / d if d > 0 else 0.0

    def remove_top(self, x, y, r):
        Vr = self.V[:, :r]; f = lambda q: q - (q @ Vr) @ Vr.T
        return cos(f(self.q[x]), f(self.q[y]))


def dev_vectors(P, pages_bif, group):
    """deviation from the norm of the group (same hand, or same hand and section), the four pages of the bifolium left out"""
    pg0 = pages_bif[0]; key = lambda p: (P[p]['H'],) if group == 'hand' else (P[p]['H'], P[p]['S'])
    norm_pages = [p for p in P if key(p) == key(pg0) and p not in pages_bif and P[p]['lines']]
    if len(norm_pages) < MINPAGES + 1:
        return None
    rel = {}
    for p in norm_pages + list(pages_bif):
        ws = [w for l in P[p]['lines'] for w in l]; c = Counter(ws); n = len(ws) or 1
        rel[p] = {w: v / n for w, v in c.items()}
    used = Counter(w for p in norm_pages for w in rel[p]); vocab = sorted(w for w, c in used.items() if c >= MINPAGES)
    M = np.array([[rel[p].get(w, 0.0) for w in vocab] for p in norm_pages]); mu = M.mean(0); sd = M.std(0); sd[sd == 0] = 1
    return {p: (np.array([rel[p].get(w, 0.0) for w in vocab]) - mu) / sd for p in pages_bif}


def analyse(path):
    P = read(path); B = bifolia(P); Sp = Space(P); rows = []
    for q, a, b in B:
        pg = {'ar': a + 'r', 'av': a + 'v', 'br': b + 'r', 'bv': b + 'v'}; pl = list(pg.values())
        meas = {}
        for g in ('hand', 'hand+section'):
            D = dev_vectors(P, pl, g)
            if D is not None:
                meas['DEV ' + g] = lambda x, y, D=D: cos(D[x], D[y])
        meas['LSA (Davis-Layfield)'] = Sp.lsa
        for kk in (25, 75, 150):
            lam = float(Sp.S[kk - 1] ** 2); meas[f'ridge-whitened, lambda = eigenvalue {kk}'] = lambda x, y, lam=lam: Sp.ridge(x, y, lam)
        for r in (5, 10, 25):
            meas[f'cosine without the top {r} directions'] = lambda x, y, r=r: Sp.remove_top(x, y, r)
        meas['plain TF-IDF cosine'] = lambda x, y: cos(Sp.q[x], Sp.q[y])
        rows.append(dict(bif=f'{a}|{b}', hand=P[a + 'r']['H'], sec=P[a + 'r']['S'],
                         pairs={m: {nm: f(pg[x], pg[y]) for nm, (x, y) in PAIRS.items()} for m, f in meas.items()}))
    return rows


def one(x):
    x = np.asarray(x); return float(wilcoxon(x, alternative='greater').pvalue) if len(x) > 1 and np.any(x != 0) else 1.0


io = lambda rows, m: [r['pairs'][m]['inner a-v|b-r'] - r['pairs'][m]['outer b-v|a-r'] for r in rows if m in r['pairs']]
p1 = lambda rows, m: [np.mean([r['pairs'][m][k] for k in ('leaf A a-r|a-v', 'inner a-v|b-r', 'leaf B b-r|b-v')]) - r['pairs'][m]['outer b-v|a-r'] for r in rows if m in r['pairs']]

srcs = [('real', os.path.join(NOV, 'scribe', 'manuscript_out', 'real.txt'))] + \
       [(os.path.basename(p)[:-4], p) for p in sorted(glob.glob(os.path.join(NOV, 'scribe', 'manuscript_out', 'scribe_seed*.txt')))]
ALL = {s: analyse(p) for s, p in srcs}; R = ALL['real']; SC = [s for s in ALL if s != 'real']
say('What the Davis-Layfield LSA measures (pre-registered: WHITENING_PREREG.md). Inner face (a-v|b-r) minus outer face (b-v|a-r), paired per bifolium.')
say('DEV = cosine of the pages\' deviations from their hand\'s norm (z-scores of word frequencies against the other pages of the hand).')
say('')
say('PRIMARY · DEV hand, one-sided Wilcoxon (inner greater), Holm over the two')
prim = [('all', [r for r in R]), ('hand 2', [r for r in R if r['hand'] == '2'])]
ps = [one(io(rows, 'DEV hand')) for _, rows in prim]; o = sorted(range(2), key=lambda i: ps[i]); holm = [0, 0]; run = 0
for rank, i in enumerate(o):
    run = max(run, min(1, (2 - rank) * ps[i])); holm[i] = run
for (lab, rows), p, h in zip(prim, ps, holm):
    d = io(rows, 'DEV hand'); scd = [io([r for r in ALL[s] if lab == 'all' or r['hand'] == '2'], 'DEV hand') for s in SC]
    say(f"  {lab:6} n {len(d):2d}: {np.mean(d):+.4f}, {100*np.mean(np.array(d) > 0):.0f}% > 0, p {p:.4f}, Holm {h:.4f} -> {'HOLDS' if h < 0.05 else 'not met'}"
        f"   | scribe {np.mean([np.mean(x) for x in scd]):+.4f} (p {min(one(x) for x in scd):.2f}-{max(one(x) for x in scd):.2f})")
say('')
say('SECONDARY · inner - outer (one-sided p) | P1 pairs written one after the other - outer (p); real, then scribe mean and p range')
for m in dict.fromkeys(m for r in R for m in r['pairs']):   # every measure, in order (not all bifolia have every DEV norm)
    for lab, sel in (('all', lambda r: True), ('hand 2', lambda r: r['hand'] == '2')):
        rr = [r for r in R if sel(r)]; d = io(rr, m); e = p1(rr, m)
        scd = [io([r for r in ALL[s] if sel(r)], m) for s in SC]
        say(f"  {m:44} {lab:6} n {len(d):2d} | inner-outer {np.mean(d):+.4f} (p {one(d):.3f}) | P1 {np.mean(e):+.4f} (p {one(e):.3f}) | scribe inner-outer {np.mean([np.mean(x) for x in scd]):+.4f} (p {min(one(x) for x in scd):.2f}-{max(one(x) for x in scd):.2f})")
open(os.path.join(HERE, 'lsa_whitening.txt'), 'w', encoding='utf-8').write('\n'.join(OUT) + '\n')
json.dump(ALL, open(os.path.join(HERE, 'lsa_whitening.json'), 'w', encoding='utf-8'), indent=1)
