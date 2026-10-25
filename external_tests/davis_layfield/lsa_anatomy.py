# What does the LSA see that the shared vocabulary does not? Anatomy of the within-bifolium asymmetry (inner face a-v|b-r more
# similar than outer face b-v|a-r: +0.096 with LSA, ~0 with every direct measure; bifolium_asymmetry2.py, singulion_vs_nesting.py).
# Folding a page into the Davis-Layfield space is v = q U_k / S_k, so the dot product of two pages is q_x M q_y with
# M = U_k S_k^-2 U_k^T, a word-by-word matrix. The LSA therefore counts (a) shared words (the diagonal of M) and (b) pairs of
# *different* words that co-vary across documents (off the diagonal), and the division by S_k^2 inflates the weak dimensions.
#   1  diagonal against off-diagonal part of the inner-outer difference
#   2  per-dimension contributions; folding variants (q U/S, q U, q U S) and k
#   3  words and word pairs that carry the difference; removing the top words
#   4  bifolia that carry it (hand, section, quire, text length); leave-one-out
#   5  parchment colour of the two faces from the Beinecke scans (a weak proxy for hair/flesh side), if the images are given
#   6  direct test of 3b: one-glyph variants (not the same word) shared across the two pages
#   7  the free choices, per hand
#   PYTHONIOENCODING=utf-8 py -3 external_tests/davis_layfield/lsa_anatomy.py [--images <folder with f1r.jpg ...>]
# Input: scribe/manuscript_out/{real,scribe_seed*}.txt. Output: here, lsa_anatomy.{txt,json}
import os, re, sys, glob, json, math
import numpy as np
from collections import Counter, defaultdict
from scipy.stats import wilcoxon, spearmanr, mannwhitneyu
HERE = os.path.dirname(os.path.abspath(__file__)); NOV = os.path.abspath(os.path.join(HERE, '..', '..'))
IMG = sys.argv[sys.argv.index('--images') + 1] if '--images' in sys.argv else None
CHUNK, MINREM, K = 40, 20, 75
QUIRES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'M', 'T']
OUT = []


def say(s=''):
    OUT.append(s); print(s, flush=True)


def pages(path):
    P = {}; cur = None
    for ln in open(path, encoding='utf-8'):
        if ln.startswith('#') or not ln.strip():
            continue
        m = re.match(r'^<(f\d+[rv]\d*)>\s+<!(.*)>', ln)
        if m:
            cur = m.group(1); v = dict(re.findall(r'\$(\w)=(\S+)', m.group(2))); P[cur] = dict(v, words=[]); continue
        m = re.match(r'^<[^>]+>\s*(.*)$', ln.rstrip('\n'))
        if not m or cur is None:
            continue
        t = m.group(1).replace('<%>', '').replace('<$>', '').replace('<->', '.')
        P[cur]['words'] += [w for w in t.split('.') if w]
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
            if all(f + x in P and P[f + x]['words'] for f in (a, b) for x in 'rv'):
                out.append((q, a, b))
    return sorted(out, key=lambda t: fnum(t[1]))


class Space:
    def __init__(self, P):
        docs = [d['words'][i:i + CHUNK] for d in P.values() for i in range(0, len(d['words']), CHUNK) if len(d['words'][i:i + CHUNK]) >= MINREM]
        df = Counter()
        for c in docs:
            df.update(set(c))
        self.terms = sorted(t for t in df if df[t] >= 2); self.ix = {t: i for i, t in enumerate(self.terms)}
        N = len(docs); self.idf = np.array([math.log(N / df[t]) for t in self.terms]); self.df = df
        A = np.zeros((len(self.terms), N))
        for j, c in enumerate(docs):
            for w, n in Counter(c).items():
                if w in self.ix:
                    A[self.ix[w], j] = n
        A *= self.idf[:, None]
        self.U, self.S, _ = np.linalg.svd(A, full_matrices=False)
        self.q = {pg: self.tfidf(d['words']) for pg, d in P.items()}
        self.tok = Counter(w for d in P.values() for w in d['words'])

    def tfidf(self, ws):
        q = np.zeros(len(self.terms))
        for w, n in Counter(ws).items():
            if w in self.ix:
                q[self.ix[w]] = n
        return q * self.idf

    def vec(self, pg, k=K, fold='inv', drop=None):
        q = self.q[pg]
        if drop is not None:
            q = q.copy(); q[drop] = 0
        v = q @ self.U[:, :k]
        return v / self.S[:k] if fold == 'inv' else (v * self.S[:k] if fold == 'mul' else v)


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb)) if na > 0 and nb > 0 else 0.0


INNER = lambda a, b: (a + 'v', b + 'r')
OUTER = lambda a, b: (b + 'v', a + 'r')


def paired(Sp, B, **kw):
    V = {}
    def v(pg):
        if pg not in V:
            V[pg] = Sp.vec(pg, **kw)
        return V[pg]
    return np.array([cos(*map(v, INNER(a, b))) - cos(*map(v, OUTER(a, b))) for q, a, b in B])


def stat(d):
    d = np.asarray(d); p = float(wilcoxon(d).pvalue) if np.any(d != 0) else 1.0
    return dict(mean=float(d.mean()), p=p, pos=float(np.mean(d > 0)), n=len(d))


def fmt(s):
    return f"{s['mean']:+.3f} (p {s['p']:.3f}, {100*s['pos']:.0f}% > 0)"


srcs = [('real', os.path.join(NOV, 'scribe', 'manuscript_out', 'real.txt'))] + \
       [(os.path.basename(p)[:-4], p) for p in sorted(glob.glob(os.path.join(NOV, 'scribe', 'manuscript_out', 'scribe_seed*.txt')))]
DATA = {}
for src, path in srcs:
    P = pages(path); DATA[src] = (P, Space(P), bifolia(P))
P, Sp, B = DATA['real']; SCR = [s for s in DATA if s != 'real']
say(f'Anatomy of the LSA inner-outer asymmetry. {len(B)} bifolia (quires {" ".join(QUIRES)}), LSA k={K}, documents of {CHUNK} words, {len(Sp.terms)} terms.')
say('Every figure is the paired difference inner face (a-v|b-r) minus outer face (b-v|a-r), per bifolium; Wilcoxon p; scribe = 5 seeds.')
say('')
RES = {}

# ---------- 1 · diagonal against off-diagonal ----------
def decompose(Sp, B, k=K):
    Uk = Sp.U[:, :k] / Sp.S[:k]; M_diag = (Uk ** 2).sum(1)
    tot, dia = [], []
    for q, a, b in B:
        r = []
        for x, y in (INNER(a, b), OUTER(a, b)):
            vx, vy = Sp.q[x] @ Uk, Sp.q[y] @ Uk; nrm = np.linalg.norm(vx) * np.linalg.norm(vy)
            r.append(((vx @ vy) / nrm, float((Sp.q[x] * M_diag * Sp.q[y]).sum()) / nrm))
        tot.append(r[0][0] - r[1][0]); dia.append(r[0][1] - r[1][1])
    tot, dia = np.array(tot), np.array(dia)
    return tot, dia, tot - dia
say('1 · Shared words (diagonal of M) against pairs of different words (off the diagonal)')
say('source | total | shared words (diagonal) | different words (off-diagonal)')
R1 = {}
for src, (P_, Sp_, B_) in DATA.items():
    t, d, o = decompose(Sp_, B_); R1[src] = dict(total=stat(t), diag=stat(d), off=stat(o))
    if src == 'real' or src == SCR[0]:
        say(f'{src} | {fmt(R1[src]["total"])} | {fmt(R1[src]["diag"])} | {fmt(R1[src]["off"])}')
say('scribe, 5 seeds (mean; p range) | ' + ' | '.join(f"{np.mean([R1[s][k]['mean'] for s in SCR]):+.3f} (p {min(R1[s][k]['p'] for s in SCR):.2f}-{max(R1[s][k]['p'] for s in SCR):.2f})" for k in ('total', 'diag', 'off')))
RES['1'] = R1; say('')

# ---------- 2 · dimensions, folding, k ----------
say('2a · Contribution of each band of LSA dimensions to the difference (real; dims ordered by singular value)')
dimc = []
for q, a, b in B:
    r = []
    for x, y in (INNER(a, b), OUTER(a, b)):
        vx, vy = Sp.vec(x), Sp.vec(y); r.append(vx * vy / (np.linalg.norm(vx) * np.linalg.norm(vy)))
    dimc.append(r[0] - r[1])
dimc = np.array(dimc)
for lo, hi in [(0, 5), (5, 10), (10, 25), (25, 50), (50, 75)]:
    say(f'  dims {lo+1}-{hi}: {fmt(stat(dimc[:, lo:hi].sum(1)))}')
top = np.argsort(-dimc.mean(0))[:8]
say('  largest single dimensions: ' + ', '.join(f'{i+1} ({dimc[:, i].mean():+.3f})' for i in top))
say(f'  share of the total carried by the 8 largest: {dimc[:, top].sum(1).mean() / dimc.sum(1).mean():.0%}')
RES['2a'] = dict(per_dim=dimc.mean(0).tolist(), top=[int(i) + 1 for i in top])
say('')
say('2b · Folding variant and k (real; scribe mean and p range)')
say('fold | k | real | scribe')
R2 = {}
for fold, lab in (('inv', 'q U/S (Davis-Layfield)'), ('none', 'q U'), ('mul', 'q U S')):
    for k in (10, 25, 50, 75, 100, 150):
        r = stat(paired(Sp, B, k=k, fold=fold)); sc = [stat(paired(DATA[s][1], DATA[s][2], k=k, fold=fold)) for s in SCR]
        R2[f'{fold}_{k}'] = dict(real=r, scribe=sc)
        say(f"{lab} | {k} | {fmt(r)} | {np.mean([x['mean'] for x in sc]):+.3f} (p {min(x['p'] for x in sc):.2f}-{max(x['p'] for x in sc):.2f})")
RES['2b'] = R2; say('')

# ---------- 3 · words and word pairs ----------
Uk = Sp.U[:, :K] / Sp.S[:K]; M = Uk @ Uk.T
term_d = np.zeros(len(Sp.terms)); pair_d = Counter()
for q, a, b in B:
    for sign, (x, y) in ((1, INNER(a, b)), (-1, OUTER(a, b))):
        qx, qy = Sp.q[x], Sp.q[y]; nrm = np.linalg.norm(qx @ Uk) * np.linalg.norm(qy @ Uk)
        term_d += sign * 0.5 * (qx * (M @ qy) + qy * (M @ qx)) / nrm
        ix, iy = np.nonzero(qx)[0], np.nonzero(qy)[0]
        C = np.outer(qx[ix], qy[iy]) * M[np.ix_(ix, iy)] / nrm
        for (i, j), c in np.ndenumerate(C):
            u, w = ix[i], iy[j]
            if u != w:
                pair_d[(min(u, w), max(u, w))] += sign * c
term_d /= len(B)
say('3a · Words that carry the difference (real): contribution to the mean inner-outer cosine, tokens in the manuscript')
order = np.argsort(-term_d)
for i in order[:20]:
    say(f'  {Sp.terms[i]:12} {term_d[i]:+.4f}  tokens {Sp.tok[Sp.terms[i]]:5d}  documents {Sp.df[Sp.terms[i]]}')
pos = np.sort(term_d[term_d > 0])[::-1]; tot = term_d.sum()
say(f'  total {tot:+.3f}; words needed for half of the positive mass: {int(np.searchsorted(np.cumsum(pos), pos.sum() / 2)) + 1} of {len(pos)} with positive contribution')
rank_tok = {t: r for r, (t, _) in enumerate(Sp.tok.most_common())}
say('  frequency rank of the 20 words: ' + ', '.join(str(rank_tok.get(Sp.terms[i], -1) + 1) for i in order[:20]))
say('')
say('3b · Pairs of different words that carry the difference (real), summed over bifolia')
for (u, w), c in sorted(pair_d.items(), key=lambda kv: -kv[1])[:20]:
    say(f'  {Sp.terms[u]:12} ~ {Sp.terms[w]:12} {c:+.4f}   M_ij {M[u, w]:+.4f}  tokens {Sp.tok[Sp.terms[u]]}/{Sp.tok[Sp.terms[w]]}')
say('')
say('3c · Removing the words that carry it (zeroed in the page vectors, same space): real; and removing the same number of top words from each scribe seed')
R3 = {}
for n in (1, 3, 5, 10, 20, 50):
    drop = order[:n]; r = stat(paired(Sp, B, drop=drop)); R3[n] = r
    rnd = [stat(paired(Sp, B, drop=np.random.default_rng(s).choice(len(Sp.terms), n, replace=False)))['mean'] for s in range(20)]
    say(f'  without the top {n:2d}: {fmt(r)}   (removing {n} random words: {np.mean(rnd):+.3f})')
fr = [Sp.ix[t] for t, _ in Sp.tok.most_common(60) if t in Sp.ix]
for n in (10, 20, 50):
    say(f'  without the {n} most frequent words of the manuscript: {fmt(stat(paired(Sp, B, drop=np.array(fr[:n]))))}')
RES['3'] = dict(top_words=[(Sp.terms[i], float(term_d[i]), Sp.tok[Sp.terms[i]]) for i in order[:40]],
                top_pairs=[(Sp.terms[u], Sp.terms[w], float(c)) for (u, w), c in sorted(pair_d.items(), key=lambda kv: -kv[1])[:40]],
                drop={str(k): v for k, v in R3.items()})
say('')

# ---------- 4 · bifolia ----------
d = paired(Sp, B); info = []
for (q, a, b), x in zip(B, d):
    pg = [a + 'r', a + 'v', b + 'r', b + 'v']
    info.append(dict(q=q, bif=f'{a}|{b}', d=float(x), hand=P[a + 'r']['H'], sec=P[a + 'r']['S'], lang=P[a + 'r']['L'],
                     w_inner=len(P[a + 'v']['words']) + len(P[b + 'r']['words']), w_outer=len(P[b + 'v']['words']) + len(P[a + 'r']['words']),
                     w_min=min(len(P[p]['words']) for p in pg)))
say('4a · Bifolia by inner-outer difference (real, LSA)')
say('  bifolium | quire | hand | section | lang | difference | words inner / outer | shortest page')
for r in sorted(info, key=lambda r: -r['d']):
    say(f"  {r['bif']:10} | {r['q']} | {r['hand']} | {r['sec']:14} | {r['lang']} | {r['d']:+.3f} | {r['w_inner']} / {r['w_outer']} | {r['w_min']}")
say('')
say('4b · By hand and by section')
for key in ('hand', 'sec', 'lang'):
    for v in sorted({r[key] for r in info}):
        x = [r['d'] for r in info if r[key] == v]
        if len(x) >= 3:
            say(f'  {key} {v}: n {len(x)}, {fmt(stat(x))}')
say('')
srt = sorted(info, key=lambda r: -r['d']); ps = []
for n in range(0, 9):
    x = [r['d'] for r in srt[n:]]; ps.append(stat(x)); say(f'4c · without the {n} largest bifolia: {fmt(ps[-1])}')
loo = [stat([r['d'] for j, r in enumerate(info) if j != i])['p'] for i in range(len(info))]
say(f'4d · leave one bifolium out: p from {min(loo):.3f} to {max(loo):.3f}')
rho = spearmanr([r['d'] for r in info], [r['w_inner'] - r['w_outer'] for r in info])
rho2 = spearmanr([r['d'] for r in info], [r['w_min'] for r in info])
say(f'4e · difference against (words inner - words outer): Spearman {rho.statistic:+.2f} (p {rho.pvalue:.3f}); against the shortest page: {rho2.statistic:+.2f} (p {rho2.pvalue:.3f})')
RES['4'] = dict(bifolia=info, loo=loo)
say('')

# ---------- 5 · parchment colour ----------
if IMG:
    from PIL import Image
    def colour(pg):
        f = os.path.join(IMG, pg + '.jpg')
        if not os.path.exists(f):
            return None
        im = np.asarray(Image.open(f).convert('RGB').resize((400, 566)), dtype=float)
        c = im[60:-60, 50:-50].reshape(-1, 3); L = c.mean(1)
        c = c[L >= np.percentile(L, 60)]   # parchment, not ink or paint
        r, g, bl = c.mean(0); return np.array([(r + g + bl) / 3, r - bl])   # brightness, warmth (red minus blue)
    rows = []
    for (q, a, b), x in zip(B, d):
        cs = {p: colour(p) for p in (a + 'r', a + 'v', b + 'r', b + 'v')}
        if all(v is not None for v in cs.values()):
            rows.append((q, a, b, x, cs))
    say(f'5 · Parchment colour of the two faces ({len(rows)} bifolia with all four scans). Brightness and warmth (R-B) of the lightest 60% of each page.')
    # validity: are the two pages of the same face of the sheet closer in colour than pages of different faces?
    same, diff = [], []
    for q, a, b, x, cs in rows:
        for i in (0, 1):
            same.append(abs(cs[a + 'v'][i] - cs[b + 'r'][i]) + abs(cs[b + 'v'][i] - cs[a + 'r'][i]))
            diff.append(abs(cs[a + 'v'][i] - cs[a + 'r'][i]) + abs(cs[b + 'r'][i] - cs[b + 'v'][i]))
    same, diff = np.array(same).reshape(-1, 2), np.array(diff).reshape(-1, 2)
    for i, nm in enumerate(('brightness', 'warmth')):
        say(f'  {nm}: |difference| between pages of the same face {same[:, i].mean():.2f}, of different faces (same leaf) {diff[:, i].mean():.2f}, paired p {wilcoxon(same[:, i] - diff[:, i]).pvalue:.3f}')
    face = [(cs[a + 'v'] + cs[b + 'r']) / 2 - (cs[b + 'v'] + cs[a + 'r']) / 2 for q, a, b, x, cs in rows]
    dd = [x for q, a, b, x, cs in rows]
    for i, nm in enumerate(('brightness', 'warmth')):
        r = spearmanr(dd, [f[i] for f in face])
        say(f'  LSA difference against (inner face - outer face) {nm}: Spearman {r.statistic:+.2f} (p {r.pvalue:.3f}); inner face {"brighter" if i == 0 else "warmer"} in {np.mean([f[i] > 0 for f in face]):.0%} of the bifolia')
    RES['5'] = dict(n=len(rows), face=[f.tolist() for f in face], d=dd)

# ---------- 6 · direct test of what 3b suggests: one-glyph variants (not the same word) across the two pages ----------
def lev1(a, b):
    if a == b or abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    if len(a) > len(b):
        a, b = b, a
    i = 0
    while i < len(a) and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


def variants(P_, B_, lo, hi):
    pf = Counter(w for d in P_.values() for w in set(d['words'])); T = {pg: {w for w in d['words'] if lo <= pf[w] <= hi} for pg, d in P_.items()}
    def sim(x, y):
        X, Y = T[x], T[y]
        n = sum(1 for w in X if any(lev1(w, v) for v in Y)) + sum(1 for v in Y if any(lev1(v, w) for w in X))
        return n / (len(X) + len(Y)) if X and Y else 0.0
    return [(P_[a + 'r']['H'], P_[a + 'r']['L'], sim(*INNER(a, b)) - sim(*OUTER(a, b))) for q, a, b in B_]
say('6 · One-glyph variants across pages (types with a distance-1 variant that is not the same word on the other page), by pages using the word')
say('band | source | all | hand 2 | Currier B')
for lo, hi in [(2, 40), (2, 10), (11, 40), (2, 9999)]:
    for src, (P_, Sp_, B_) in DATA.items():
        r = variants(P_, B_, lo, hi)
        say(f"{lo}-{hi} | {src} | {fmt(stat([x[2] for x in r]))} | {fmt(stat([x[2] for x in r if x[0] == '2']))} | {fmt(stat([x[2] for x in r if x[1] == 'B']))}")
say('')

# ---------- 7 · the free choices, per hand (bifolium_asymmetry2.py looked at them only together) ----------
def rates(ws):
    n = len(ws) or 1; k = sum(w.count('k') for w in ws); t = sum(w.count('t') for w in ws); ch = sum(w.count('ch') for w in ws); sh = sum(w.count('sh') for w in ws)
    y = sum(w.endswith('y') for w in ws)
    return np.array([sum(w.startswith('q') for w in ws) / n, k / (k + t) if k + t else .5, ch / (ch + sh) if ch + sh else .5,
                     sum(w.endswith('dy') for w in ws) / y if y else .5, sum('e' in w for w in ws) / n])
say('7 · Free choices, outer-face distance minus inner-face distance (> 0: inner face closer), mean / Wilcoxon p, per hand')
say('source | group | q- | k/(k+t) | ch/(ch+sh) | -dy/-y | e words')
for src, (P_, Sp_, B_) in DATA.items():
    R_ = {pg: rates(d['words']) for pg, d in P_.items()}
    for grp in ('all', '1', '2', '3'):
        sel = [(a, b) for q, a, b in B_ if grp == 'all' or P_[a + 'r']['H'] == grp]
        dd_ = np.array([np.abs(R_[b + 'v'] - R_[a + 'r']) - np.abs(R_[a + 'v'] - R_[b + 'r']) for a, b in sel])
        say(f'{src} | {grp} (n {len(sel)}) | ' + ' | '.join(f"{dd_[:, i].mean():+.3f} / {wilcoxon(dd_[:, i]).pvalue if np.any(dd_[:, i]) else 1:.2f}" for i in range(5)))
open(os.path.join(HERE, 'lsa_anatomy.txt'), 'w', encoding='utf-8').write('\n'.join(OUT) + '\n')
json.dump(RES, open(os.path.join(HERE, 'lsa_anatomy.json'), 'w', encoding='utf-8'), indent=1, default=float)
