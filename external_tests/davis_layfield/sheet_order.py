# Writing order within the sheet (pre-registered in SHEET_ORDER_PREREG.md). Six page pairs of each bifolium, with three measures
# that are not the LSA (glyph trigrams G3, glyph-bigram cross-entropy gain XE, NMF topics) and the LSA for reference; tests
# P1 (time: pairs written one after the other > outer face), P2 (sight: inner face > the two leaves) and P3 (continuity across the
# page turn, with half pages).
#   PYTHONIOENCODING=utf-8 py -3 external_tests/davis_layfield/sheet_order.py
# Input: scribe/manuscript_out/{real,scribe_seed*}.txt. Output: here, sheet_order.{txt,json}
import os, re, glob, json, math, warnings
import numpy as np
from collections import Counter, defaultdict
from scipy.stats import wilcoxon
from sklearn.decomposition import NMF
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); NOV = os.path.abspath(os.path.join(HERE, '..', '..'))
QUIRES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'M', 'T']
CHUNK, MINREM, K = 40, 20, 75
PAIRS = {'leaf A a-r|a-v': ('ar', 'av'), 'inner a-v|b-r': ('av', 'br'), 'leaf B b-r|b-v': ('br', 'bv'),
         'diag a-r|b-r': ('ar', 'br'), 'diag a-v|b-v': ('av', 'bv'), 'outer b-v|a-r': ('bv', 'ar')}
TRANS = [('ar', 'av'), ('av', 'br'), ('br', 'bv')]
MEASURES = ['G3', 'XE', 'NMF', 'LSA']
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


def fnum(f):
    return int(re.match(r'f(\d+)', f).group(1))


def bifolia(P):
    sheets = defaultdict(set)
    for pg, d in P.items():
        m = re.fullmatch(r'(f\d+)[rv]', pg)
        if m and d['Q'] in QUIRES:
            sheets[(d['Q'], d['F'])].add(m.group(1))
    out = []
    for (q, s), fs in sheets.items():
        if len(fs) == 2:
            a, b = sorted(fs, key=fnum)
            if all(f + x in P and P[f + x]['lines'] for f in (a, b) for x in 'rv'):
                out.append((q, a, b))
    return sorted(out, key=lambda t: fnum(t[1]))


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb)) if na > 0 and nb > 0 else 0.0


class Measures:
    """all four similarities, built on the whole manuscript of one source"""
    def __init__(self, P):
        pages = {pg: [w for l in d['lines'] for w in l] for pg, d in P.items()}
        # G3: glyph trigrams with boundary marks, idf over pages
        self.tri_df = Counter()
        for ws in pages.values():
            self.tri_df.update({t for w in ws for t in self.tris(w)})
        self.tri = {t: i for i, t in enumerate(sorted(self.tri_df))}; Np = len(pages)
        self.tri_idf = np.array([math.log(Np / self.tri_df[t]) for t in sorted(self.tri_df)])
        # XE: background glyph-bigram model
        self.bg = Counter(); self.bg1 = Counter()
        for ws in pages.values():
            for w in ws:
                for a, b in self.bis(w):
                    self.bg[(a, b)] += 1; self.bg1[a] += 1
        self.alpha = sorted({c for (a, b) in self.bg for c in (a, b)}); self.V = len(self.alpha)
        # word space for LSA and NMF: 40-word documents, TF-IDF
        docs = [ws[i:i + CHUNK] for ws in pages.values() for i in range(0, len(ws), CHUNK) if len(ws[i:i + CHUNK]) >= MINREM]
        df = Counter()
        for c in docs:
            df.update(set(c))
        terms = sorted(t for t in df if df[t] >= 2); self.ix = {t: i for i, t in enumerate(terms)}
        self.idf = np.array([math.log(len(docs) / df[t]) for t in terms])
        A = np.array([self.tfidf(c) for c in docs])
        U, S, _ =np.linalg.svd(A.T, full_matrices=False); self.Uk, self.Sk = U[:, :K], S[:K]
        self.nmf = NMF(n_components=20, init='nndsvda', random_state=0, max_iter=600).fit(A)

    @staticmethod
    def tris(w):
        s = '^' + w + '$'; return [s[i:i + 3] for i in range(len(s) - 2)]

    @staticmethod
    def bis(w):
        s = '^' + w + '$'; return list(zip(s, s[1:]))

    def tfidf(self, ws):
        q = np.zeros(len(self.ix))
        for w, n in Counter(ws).items():
            if w in self.ix:
                q[self.ix[w]] = n
        return q * self.idf

    def g3(self, ws):
        v = np.zeros(len(self.tri))
        for w in ws:
            for t in self.tris(w):
                if t in self.tri:
                    v[self.tri[t]] += 1
        return v * self.tri_idf

    def xe_gain(self, X, Y):
        """bits per glyph saved on Y by the model of X against the background (add-0.5 towards the background)"""
        c = Counter(); c1 = Counter()
        for w in X:
            for a, b in self.bis(w):
                c[(a, b)] += 1; c1[a] += 1
        g = []; m = 0.5 * self.V
        for w in Y:
            for a, b in self.bis(w):
                pb = (self.bg[(a, b)] + 0.5) / (self.bg1[a] + m)
                px = (c[(a, b)] + m * pb) / (c1[a] + m)
                g.append(math.log2(px / pb))
        return float(np.mean(g)) if g else 0.0

    def vectors(self, ws):
        q = self.tfidf(ws)
        return dict(G3=self.g3(ws), NMF=self.nmf.transform(q[None, :])[0], LSA=(q @ self.Uk) / self.Sk, words=ws)

    def sim(self, a, b, m):
        if m == 'XE':
            return 0.5 * (self.xe_gain(a['words'], b['words']) + self.xe_gain(b['words'], a['words']))
        return cos(a[m], b[m])


def analyse(path):
    P = read(path); B = bifolia(P); Ms = Measures(P); rows = []
    for q, a, b in B:
        pg = {'ar': a + 'r', 'av': a + 'v', 'br': b + 'r', 'bv': b + 'v'}
        full = {k: Ms.vectors([w for l in P[v]['lines'] for w in l]) for k, v in pg.items()}
        half = {}
        for k, v in pg.items():
            L = P[v]['lines']; h = (len(L) + 1) // 2
            half[k] = (Ms.vectors([w for l in L[:h] for w in l]), Ms.vectors([w for l in L[h:] for w in l]))
        r = dict(q=q, bif=f'{a}|{b}', hand=P[a + 'r']['H'], pairs={}, C={}, Cctl={})
        for m in MEASURES:
            r['pairs'][m] = {nm: Ms.sim(full[x], full[y], m) for nm, (x, y) in PAIRS.items()}
            def C(x, y):
                (xt, xb), (yt, yb) = half[x], half[y]
                return Ms.sim(xb, yt, m) - 0.5 * (Ms.sim(xt, yt, m) + Ms.sim(xb, yb, m))
            r['C'][m] = float(np.mean([C(x, y) for x, y in TRANS])); r['Cctl'][m] = C('bv', 'ar')
        rows.append(r)
    return rows


def contrasts(rows, m):
    p = lambda r, k: r['pairs'][m][k]
    P1 = [np.mean([p(r, 'leaf A a-r|a-v'), p(r, 'inner a-v|b-r'), p(r, 'leaf B b-r|b-v')]) - p(r, 'outer b-v|a-r') for r in rows]
    P2 = [p(r, 'inner a-v|b-r') - 0.5 * (p(r, 'leaf A a-r|a-v') + p(r, 'leaf B b-r|b-v')) for r in rows]
    P3 = [r['C'][m] for r in rows]; P3c = [r['Cctl'][m] for r in rows]
    return dict(P1=P1, P2=P2, P3=P3, P3ctl=P3c)


def one(x):
    x = np.asarray(x); return float(wilcoxon(x, alternative='greater').pvalue) if np.any(x != 0) else 1.0


srcs = [('real', os.path.join(NOV, 'scribe', 'manuscript_out', 'real.txt'))] + \
       [(os.path.basename(p)[:-4], p) for p in sorted(glob.glob(os.path.join(NOV, 'scribe', 'manuscript_out', 'scribe_seed*.txt')))]
ALL = {s: analyse(p) for s, p in srcs}
SC = [s for s in ALL if s != 'real']; R = ALL['real']
say('Writing order within the sheet (pre-registered: SHEET_ORDER_PREREG.md). 37 bifolia; G3 = glyph trigrams, XE = cross-entropy gain (bits/glyph), NMF = 20 topics, LSA for reference.')
say('')
say('Mean similarity of the six pairs (real | scribe, mean of 5 seeds)')
say('pair | ' + ' | '.join(MEASURES))
for nm in PAIRS:
    say(f'{nm:16} | ' + ' | '.join(f"{np.mean([r['pairs'][m][nm] for r in R]):.3f} | {np.mean([np.mean([r['pairs'][m][nm] for r in ALL[s]]) for s in SC]):.3f}" for m in MEASURES))
say('')
say('PRIMARY · one-sided Wilcoxon (greater), all bifolia; Holm over the six tests (P1, P2, P3 × G3, XE)')
prim = []
for m in ('G3', 'XE'):
    c = contrasts(R, m)
    for k in ('P1', 'P2', 'P3'):
        prim.append((f'{k} {m}', one(c[k]), float(np.mean(c[k])), float(np.mean(np.array(c[k]) > 0))))
order = sorted(range(len(prim)), key=lambda i: prim[i][1]); holm = [None] * len(prim); run = 0
for rank, i in enumerate(order):
    run = max(run, min(1.0, (len(prim) - rank) * prim[i][1])); holm[i] = run
for (nm, p, mn, pos), h in zip(prim, holm):
    say(f'  {nm:7} mean {mn:+.4f}, {100*pos:.0f}% > 0, p {p:.4f}, Holm {h:.4f} -> {"HOLDS" if h < 0.05 else "not met"}')
say('')
say('SECONDARY · all measures: real mean (one-sided p) | scribe: mean of seeds, p range')
for m in MEASURES:
    cr = contrasts(R, m); cs = [contrasts(ALL[s], m) for s in SC]
    say(f'  {m:3} ' + ' | '.join(f"{k} {np.mean(cr[k]):+.4f} (p {one(cr[k]):.3f}) / scribe {np.mean([np.mean(c[k]) for c in cs]):+.4f} (p {min(one(c[k]) for c in cs):.2f}-{max(one(c[k]) for c in cs):.2f})" for k in ('P1', 'P2', 'P3', 'P3ctl')))
say('')
say('SECONDARY · by hand (real): mean (one-sided p)')
for h in ('1', '2', '3'):
    rr = [r for r in R if r['hand'] == h]
    for m in MEASURES:
        c = contrasts(rr, m)
        say(f'  hand {h} (n {len(rr):2d}) {m:3} ' + ' | '.join(f"{k} {np.mean(c[k]):+.4f} (p {one(c[k]):.3f})" for k in ('P1', 'P2', 'P3', 'P3ctl')))

# ---------- validation (added after the primary run; not pre-registered): can the measures see drift at this scale at all? ----------
# Each page of the 37 bifolia with >= 6 lines split into thirds by lines: mean of the two adjacent thirds minus the two far thirds.
say('')
say('VALIDATION (not pre-registered) · within a page, thirds: (adjacent thirds) - (top vs bottom third), one-sided p')
for src, path in srcs[:4]:
    P = read(path); B = bifolia(P); Ms = Measures(P); D = {m: [] for m in MEASURES}
    for q, a, b in B:
        for pg in (a + 'r', a + 'v', b + 'r', b + 'v'):
            L = P[pg]['lines']
            if len(L) < 6:
                continue
            t = len(L) // 3; V = [Ms.vectors([w for l in x for w in l]) for x in (L[:t], L[t:2 * t], L[2 * t:])]
            for m in D:
                D[m].append(0.5 * (Ms.sim(V[0], V[1], m) + Ms.sim(V[1], V[2], m)) - Ms.sim(V[0], V[2], m))
    say(f'  {src:13} ' + ' | '.join(f"{m} {np.mean(v):+.4f} (p {one(v):.4f}, n {len(v)})" for m, v in D.items()))
open(os.path.join(HERE, 'sheet_order.txt'), 'w', encoding='utf-8').write('\n'.join(OUT) + '\n')
json.dump(ALL, open(os.path.join(HERE, 'sheet_order.json'), 'w', encoding='utf-8'), indent=1)
