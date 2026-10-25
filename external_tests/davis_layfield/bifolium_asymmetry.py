# Companion to lsa_singulion.py: within the bifolium, which pairs of pages are most alike? If the bifolium is written in the order
# a-r, a-v, b-r, b-v (the reading order of a singulion), the writing distance between two pages is 1 (a-r|a-v, a-v|b-r,
# b-r|b-v), 2 (a-r|b-r, a-v|b-v) or 3 (b-v|a-r). Also: position of the bifolium in the quire (outer -> central), paired test
# conjoint - outer, and the singulion reordering as Davis and Layfield do it (only the junctions between bifolia).
#   PYTHONIOENCODING=utf-8 py -3 external_tests/davis_layfield/bifolium_asymmetry.py [--k 75]
import os, re, sys, glob, json, math, itertools
import numpy as np
from collections import Counter, defaultdict
from scipy.stats import wilcoxon
HERE = os.path.dirname(os.path.abspath(__file__)); NOV = os.path.abspath(os.path.join(HERE, '..', '..'))
K = int(sys.argv[sys.argv.index('--k') + 1]) if '--k' in sys.argv else 75
CHUNK, MINREM = 40, 20
QUIRES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'M', 'T']
PAIRS = [('a-r|a-v', 1), ('a-v|b-r', 1), ('b-r|b-v', 1), ('a-r|b-r', 2), ('a-v|b-v', 2), ('b-v|a-r', 3)]
rng = np.random.default_rng(0)


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


def lsa(P, k):
    docs = [d['words'][i:i + CHUNK] for d in P.values() for i in range(0, len(d['words']), CHUNK) if len(d['words'][i:i + CHUNK]) >= MINREM]
    df = Counter()
    for c in docs:
        df.update(set(c))
    terms = sorted(t for t in df if df[t] >= 2); ix = {t: i for i, t in enumerate(terms)}
    N = len(docs); idf = np.array([math.log(N / df[t]) for t in terms])
    A = np.zeros((len(terms), N))
    for j, c in enumerate(docs):
        for w, n in Counter(c).items():
            if w in ix:
                A[ix[w], j] = n
    A *= idf[:, None]
    U, S, _ = np.linalg.svd(A, full_matrices=False); Uk = U[:, :k]; Sk = S[:k]

    def fold(ws):
        q = np.zeros(len(terms))
        for w, n in Counter(ws).items():
            if w in ix:
                q[ix[w]] = n
        return (q * idf @ Uk) / Sk
    return {pg: fold(d['words']) for pg, d in P.items()}


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb)) if na > 0 and nb > 0 else float('nan')


def fnum(f):
    return int(re.match(r'f(\d+)', f).group(1))


def bifolis(P):
    """quire -> list of (a, b) ordered from outer to central"""
    sheets = defaultdict(set)
    for pg, d in P.items():
        m = re.fullmatch(r'(f\d+)[rv]', pg)
        if m and d['Q'] in QUIRES:
            sheets[(d['Q'], d['F'])].add(m.group(1))
    byq = defaultdict(list)
    for (q, s), fs in sheets.items():
        if len(fs) == 2:
            byq[q].append(tuple(sorted(fs, key=fnum)))
    return {q: sorted(bl, key=lambda ab: fnum(ab[0])) for q, bl in byq.items()}


def pair_pages(a, b, name):
    x, y = name.split('|'); f = {'a': a, 'b': b}
    return f[x[0]] + x[2], f[y[0]] + y[2]


def boot_ci(v, n=4000):
    v = np.array(v); m = [rng.choice(v, len(v)).mean() for _ in range(n)]
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def reorder_junctions(bl, vec):
    """Davis-Layfield: current = mean facing of the nested order; best = maximum over permutations of the mean facing at the junctions b_i-v | a_i+1-r"""
    folios = sorted({f for ab in bl for f in ab}, key=fnum)
    cur = float(np.mean([cos(vec[f1 + 'v'], vec[f2 + 'r']) for f1, f2 in zip(folios, folios[1:]) if f1 + 'v' in vec and f2 + 'r' in vec]))
    def junc(seq):
        s = [cos(vec[x[1] + 'v'], vec[y[0] + 'r']) for x, y in zip(seq, seq[1:]) if x[1] + 'v' in vec and y[0] + 'r' in vec]
        return float(np.mean(s))
    allp = sorted(((junc(seq), seq) for seq in itertools.permutations(bl)), reverse=True)
    best, bseq = allp[0]
    return dict(current=cur, best=best, gain_pct=100 * (best / cur - 1), median_perm=float(np.median([s for s, _ in allp])),
                nested_junctions=junc(tuple(bl)), best_seq=', '.join(f'{a[1:]}|{b[1:]}' for a, b in bseq))


def analyse(path):
    P = pages(path); vec = lsa(P, K); B = bifolis(P)
    rows = []   # (quire, position, pair name, distance, cosine)
    for q, bl in B.items():
        n = len(bl)
        for i, (a, b) in enumerate(bl):
            pos = 'central' if i == n - 1 else ('exterior' if i == 0 else 'middle')
            for name, d in PAIRS:
                x, y = pair_pages(a, b, name)
                if x in vec and y in vec:
                    rows.append((q, pos, name, d, cos(vec[x], vec[y])))
    res = {'per_parell': {}, 'per_distancia': {}, 'per_posicio': {}}
    for name, d in PAIRS:
        v = [c for q, p, nm, dd, c in rows if nm == name]; res['per_parell'][name] = dict(mean=float(np.mean(v)), n=len(v), ci=boot_ci(v))
    for d in (1, 2, 3):
        v = [c for q, p, nm, dd, c in rows if dd == d]; res['per_distancia'][d] = dict(mean=float(np.mean(v)), n=len(v), ci=boot_ci(v))
    for pos in ('exterior', 'middle', 'central'):
        res['per_posicio'][pos] = {nm: float(np.mean([c for q, p, n2, dd, c in rows if p == pos and n2 == nm])) for nm in ('a-v|b-r', 'b-v|a-r', 'a-r|a-v')}
        res['per_posicio'][pos]['n'] = len([1 for q, p, n2, dd, c in rows if p == pos and n2 == 'a-v|b-r'])
    # paired per bifolium: conjoint (a-v|b-r) minus outer (b-v|a-r); and conjoint minus the mean of the two confoliate of the same bifolium
    by = defaultdict(dict)
    for q, p, nm, dd, c in rows:
        by[(q, p, nm)]  # no-op
    bif_vals = defaultdict(dict)
    for q, bl in B.items():
        for a, b in bl:
            for name, d in PAIRS:
                x, y = pair_pages(a, b, name)
                if x in vec and y in vec:
                    bif_vals[(q, a, b)][name] = cos(vec[x], vec[y])
    d_co = [v['a-v|b-r'] - v['b-v|a-r'] for v in bif_vals.values() if 'a-v|b-r' in v and 'b-v|a-r' in v]
    d_cc = [v['a-v|b-r'] - (v['a-r|a-v'] + v['b-r|b-v']) / 2 for v in bif_vals.values() if all(k in v for k in ('a-v|b-r', 'a-r|a-v', 'b-r|b-v'))]
    res['aparellat'] = {'conjoint-outer': dict(mean=float(np.mean(d_co)), n=len(d_co), p_wilcoxon=float(wilcoxon(d_co).pvalue), frac_pos=float(np.mean(np.array(d_co) > 0))),
                        'conjoint-confoliate': dict(mean=float(np.mean(d_cc)), n=len(d_cc), p_wilcoxon=float(wilcoxon(d_cc).pvalue), frac_pos=float(np.mean(np.array(d_cc) > 0)))}
    res['reorder'] = {q: reorder_junctions(B[q], vec) for q in ('M', 'T') if q in B}
    return res


srcs = [('real', os.path.join(NOV, 'scribe', 'manuscript_out', 'real.txt'))] + \
       [(os.path.basename(p)[:-4], p) for p in sorted(glob.glob(os.path.join(NOV, 'scribe', 'manuscript_out', 'scribe_seed*.txt')))]
ALL = {s: analyse(p) for s, p in srcs}
sc = [r for s, r in ALL.items() if s.startswith('scribe')]
L = [f'Within the bifolium (LSA k={K}, quires {" ".join(QUIRES)}); assumed writing order a-r, a-v, b-r, b-v', '',
     'pair (distance) | real [95% CI] | scribe mean of 5 seeds ± SD']
for name, d in PAIRS:
    r = ALL['real']['per_parell'][name]; m = [x['per_parell'][name]['mean'] for x in sc]
    L.append(f'{name} ({d}) | {r["mean"]:.3f} [{r["ci"][0]:.3f}, {r["ci"][1]:.3f}] n={r["n"]} | {np.mean(m):.3f} ± {np.std(m):.3f}')
L += ['', 'distance | real [95% CI] | scribe']
for d in (1, 2, 3):
    r = ALL['real']['per_distancia'][d]; m = [x['per_distancia'][d]['mean'] for x in sc]
    L.append(f'{d} | {r["mean"]:.3f} [{r["ci"][0]:.3f}, {r["ci"][1]:.3f}] n={r["n"]} | {np.mean(m):.3f} ± {np.std(m):.3f}')
L += ['', 'bifolium position | n | real conjoint / outer / confoliate(a) | scribe conjoint / outer / confoliate(a)']
for pos in ('exterior', 'middle', 'central'):
    r = ALL['real']['per_posicio'][pos]
    L.append(f'{pos} | {r["n"]} | {r["a-v|b-r"]:.3f} / {r["b-v|a-r"]:.3f} / {r["a-r|a-v"]:.3f} | ' +
             ' / '.join(f'{np.mean([x["per_posicio"][pos][k] for x in sc]):.3f}' for k in ('a-v|b-r', 'b-v|a-r', 'a-r|a-v')))
L += ['', 'paired per bifolium | real: mean, Wilcoxon p, fraction > 0 | scribe (5 seeds): mean, min and max p']
for k in ('conjoint-outer', 'conjoint-confoliate'):
    r = ALL['real']['aparellat'][k]; ps = [x['aparellat'][k]['p_wilcoxon'] for x in sc]; ms = [x['aparellat'][k]['mean'] for x in sc]
    L.append(f'{k} | {r["mean"]:+.3f}, p={r["p_wilcoxon"]:.3f}, {100*r["frac_pos"]:.0f}% (n={r["n"]}) | {np.mean(ms):+.3f}, p {min(ps):.2f}-{max(ps):.2f}')
L += ['', 'Reordering in the Davis-Layfield manner (current = facing of the nested order; best = junctions between bifolia, maximum over permutations):',
      'source | quire | current | junctions of the nested order | best | gain % | median of permutations | best sequence']
for s, r in ALL.items():
    for q, d in r['reorder'].items():
        L.append(f'{s} | {q} | {d["current"]:.3f} | {d["nested_junctions"]:.3f} | {d["best"]:.3f} | {d["gain_pct"]:.1f} | {d["median_perm"]:.3f} | {d["best_seq"]}')
for q in ('M', 'T'):
    g = [x['reorder'][q]['gain_pct'] for x in sc]
    L.append(f'  {q}: real gain {ALL["real"]["reorder"][q]["gain_pct"]:.1f}% · scribe {np.mean(g):.1f} ± {np.std(g):.1f}% (Davis-Layfield: M 12.1%, T 20%)')
open(os.path.join(HERE, f'results_asymmetry_k{K}.txt'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
json.dump(ALL, open(os.path.join(HERE, f'results_asymmetry_k{K}.json'), 'w', encoding='utf-8'), indent=1)
print('\n'.join(L))
