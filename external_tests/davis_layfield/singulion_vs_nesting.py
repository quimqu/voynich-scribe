# Koen's question (voynich.ninja, thread 6219, 10/2026): the current binding is easy to beat; does a singulion structure
# beat the best alternative *nesting*? For each quire with n complete bifolia we compare, under the same similarity measure:
#   nested (current)  the order of the bifolia as bound now, nested;
#   nested (best)     the best of all n! orders of the bifolia, nested (outer -> central);
#   singulion (best)  the best of all n! orders, each bifolium read a-r a-v b-r b-v (Davis and Layfield's reordering).
# Both structures have 2n-1 facing pairs. In a singulion n of them are the inner face of a bifolium (same sheet); in a nesting only
# the central one is. So we also report the facing pairs split into same-sheet and cross-sheet. Same on the scribe, which has sheet
# habits and no reading order: whatever the scribe also "prefers" cannot be evidence of the reading order.
#   PYTHONIOENCODING=utf-8 py -3 external_tests/davis_layfield/singulion_vs_nesting.py [--k 75]
# Input: scribe/manuscript_out/{real,scribe_seed*}.txt. Output: here, singulion_vs_nesting.{txt,json}
import os, re, sys, glob, json, math, itertools
import numpy as np
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); NOV = os.path.abspath(os.path.join(HERE, '..', '..'))
K = int(sys.argv[sys.argv.index('--k') + 1]) if '--k' in sys.argv else 75
CHUNK, MINREM = 40, 20
QUIRES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'M', 'T']


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


def spaces(P, k):
    """two page representations: LSA (Davis-Layfield) and plain TF-IDF (no SVD)"""
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

    def tfidf(ws):
        q = np.zeros(len(terms))
        for w, n in Counter(ws).items():
            if w in ix:
                q[ix[w]] = n
        return q * idf
    T = {pg: tfidf(d['words']) for pg, d in P.items()}
    Bn = {pg: (v > 0).astype(float) for pg, v in T.items()}   # shared vocabulary only (cosine of presence vectors), no weights
    return {'LSA': {pg: (v @ Uk) / Sk for pg, v in T.items()}, 'TF-IDF': T, 'types': Bn}


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb)) if na > 0 and nb > 0 else float('nan')


def fnum(f):
    return int(re.match(r'f(\d+)', f).group(1))


def bifolia(P):
    """quire -> bifolia (a, b) in the current order, outer to central; only quires whose bifolia are all complete"""
    sheets = defaultdict(set); allf = defaultdict(set)
    for pg, d in P.items():
        m = re.fullmatch(r'(f\d+)[rv]', pg)
        if m and d.get('Q') in QUIRES:
            sheets[(d['Q'], d['F'])].add(m.group(1)); allf[d['Q']].add(m.group(1))
    byq = defaultdict(list)
    for (q, s), fs in sheets.items():
        if len(fs) == 2:
            byq[q].append(tuple(sorted(fs, key=fnum)))
    out = {}
    for q, bl in byq.items():
        bl = [ab for ab in bl if all(f + s in P for f in ab for s in 'rv')]   # complete bifolia only (quire 20 has lost some)
        if len(bl) >= 3:
            out[q] = sorted(bl, key=lambda ab: fnum(ab[0]))
    return out


def facing_nested(seq):
    """seq outer -> central; facing pairs (v, r, same_sheet)"""
    n = len(seq); pr = []
    for i in range(n - 1):
        pr.append((seq[i][0] + 'v', seq[i + 1][0] + 'r', False))
    pr.append((seq[-1][0] + 'v', seq[-1][1] + 'r', True))
    for i in range(n - 1, 0, -1):
        pr.append((seq[i][1] + 'v', seq[i - 1][1] + 'r', False))
    return pr


def facing_singulion(seq):
    pr = []
    for i, (a, b) in enumerate(seq):
        pr.append((a + 'v', b + 'r', True))
        if i + 1 < len(seq):
            pr.append((b + 'v', seq[i + 1][0] + 'r', False))
    return pr


def facing_sham(seq, kind):
    """control structures with the singulion's combinatorics, but the same-sheet facing pair is another pair of the bifolium:
    'outer' = b-v|a-r, 'diag_r' = a-r|b-r, 'diag_v' = a-v|b-v, 'conf' = a-r|a-v. Not physical; they ask whether the singulion's win is
    the inner face of the sheet in particular or any two pages of the same sheet."""
    pick = {'outer': lambda a, b: (b + 'v', a + 'r'), 'diag_r': lambda a, b: (a + 'r', b + 'r'), 'diag_v': lambda a, b: (a + 'v', b + 'v'),
            'conf': lambda a, b: (a + 'r', a + 'v')}[kind]
    pr = []
    for i, (a, b) in enumerate(seq):
        pr.append(pick(a, b) + (True,))
        if i + 1 < len(seq):
            pr.append((b + 'v', seq[i + 1][0] + 'r', False))
    return pr


SHAMS = ['outer', 'diag_r', 'diag_v', 'conf']


def score(pr, vec):
    s = [cos(vec[x], vec[y]) for x, y, _ in pr]; same = [c for c, (_, _, f) in zip(s, pr) if f]; cross = [c for c, (_, _, f) in zip(s, pr) if not f]
    return float(np.mean(s)), float(np.mean(same)), float(np.mean(cross))


def analyse(P, vec, B):
    res = {}
    for q, bl in B.items():
        perms = list(itertools.permutations(bl))
        nest = [score(facing_nested(p), vec) for p in perms]; sing = [score(facing_singulion(p), vec) for p in perms]
        cur = score(facing_nested(tuple(bl)), vec)
        sham = {k: max(score(facing_sham(p, k), vec)[0] for p in perms) for k in SHAMS}
        bn = max(range(len(perms)), key=lambda i: nest[i][0]); bs = max(range(len(perms)), key=lambda i: sing[i][0])
        # the cross-sheet pairs alone: the best nesting's 2n-2 junctions against the best singulion's n-1 junctions
        res[q] = dict(sham=sham, n=len(bl), n_perm=len(perms), current=cur, best_nested=nest[bn], best_singulion=sing[bs],
                      median_nested=float(np.median([x[0] for x in nest])), median_singulion=float(np.median([x[0] for x in sing])),
                      frac_singulion_beats_best_nested=float(np.mean([x[0] > nest[bn][0] for x in sing])),
                      best_cross_nested=max(x[2] for x in nest), best_cross_singulion=max(x[2] for x in sing),
                      seq_nested=', '.join(f'{a[1:]}|{b[1:]}' for a, b in perms[bn]), seq_singulion=', '.join(f'{a[1:]}|{b[1:]}' for a, b in perms[bs]))
    return res


srcs = [('real', os.path.join(NOV, 'scribe', 'manuscript_out', 'real.txt'))] + \
       [(os.path.basename(p)[:-4], p) for p in sorted(glob.glob(os.path.join(NOV, 'scribe', 'manuscript_out', 'scribe_seed*.txt')))]
ALL = {}
for src, path in srcs:
    P = pages(path); B = bifolia(P); V = spaces(P, K)
    ALL[src] = {m: analyse(P, v, B) for m, v in V.items()}
    print(src, 'quires', ' '.join(f'{q}({len(b)})' for q, b in B.items()), flush=True)
quires = list(ALL['real']['LSA'])
L = [f'Singulion against the best nesting (LSA k={K}, TF-IDF without SVD, and shared word types; documents of {CHUNK} words). Mean cosine over the 2n-1 facing pairs.',
     'cur = nested, current order · N* = best nested order · S* = best singulion order · same/cross = facing pairs on the same sheet / across sheets', '']
for m in ('LSA', 'TF-IDF', 'types'):
    L += [f'== {m} ==', 'source | quire (n) | cur | N* | S* | S*/N* | S* same / cross | N* same / cross | best cross-sheet: N / S | median N / S']
    for src, R in ALL.items():
        for q in quires:
            d = R[m][q]
            L.append(f"{src} | {q} ({d['n']}) | {d['current'][0]:.3f} | {d['best_nested'][0]:.3f} | {d['best_singulion'][0]:.3f} | {d['best_singulion'][0]/d['best_nested'][0]:.2f} | "
                     f"{d['best_singulion'][1]:.3f} / {d['best_singulion'][2]:.3f} | {d['best_nested'][1]:.3f} / {d['best_nested'][2]:.3f} | "
                     f"{d['best_cross_nested']:.3f} / {d['best_cross_singulion']:.3f} | {d['median_nested']:.3f} / {d['median_singulion']:.3f}")
    L.append('')
    L.append('summary over quires (mean): source | cur | N* | S* | S* beats N* in | median singulion beats N* in | gain N*/cur | gain S*/N*')
    for src, R in ALL.items():
        D = [R[m][q] for q in quires]
        L.append(f"{src} | {np.mean([d['current'][0] for d in D]):.3f} | {np.mean([d['best_nested'][0] for d in D]):.3f} | {np.mean([d['best_singulion'][0] for d in D]):.3f} | "
                 f"{sum(d['best_singulion'][0] > d['best_nested'][0] for d in D)}/{len(D)} | {sum(d['median_singulion'] > d['best_nested'][0] for d in D)}/{len(D)} | "
                 f"{100*np.mean([d['best_nested'][0]/d['current'][0]-1 for d in D]):+.0f}% | {100*np.mean([d['best_singulion'][0]/d['best_nested'][0]-1 for d in D]):+.0f}%")
    L.append('')
    L.append('controls, same combinatorics as a singulion but another same-sheet pair (best order): S*/N* per quire, mean over quires')
    L.append('source | inner face (singulion) | ' + ' | '.join(SHAMS))
    for src, R in ALL.items():
        D = [R[m][q] for q in quires]
        L.append(f"{src} | {np.mean([d['best_singulion'][0]/d['best_nested'][0] for d in D]):.2f} ({sum(d['best_singulion'][0] > d['best_nested'][0] for d in D)}/{len(D)}) | " +
                 ' | '.join(f"{np.mean([d['sham'][k]/d['best_nested'][0] for d in D]):.2f} ({sum(d['sham'][k] > d['best_nested'][0] for d in D)}/{len(D)})" for k in SHAMS))
    L.append('')
open(os.path.join(HERE, 'singulion_vs_nesting.txt'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
json.dump(ALL, open(os.path.join(HERE, 'singulion_vs_nesting.json'), 'w', encoding='utf-8'), indent=1)
print('\n'.join(L))

# Rare shared words: inner face (a-v|b-r) minus outer face (b-v|a-r), paired per bifolium, by how many pages of the manuscript use
# the word. If the LSA win of the singulion were copying across the open sheet, it should show here.
from scipy.stats import wilcoxon
BANDS = [(2, 3), (4, 10), (11, 40), (41, 9999)]
L = ['Shared word types, inner face minus outer face, paired per bifolium (mean difference in number of types, Wilcoxon p), by number of pages using the word', 'source | ' + ' | '.join(f'{lo}-{hi} pages' for lo, hi in BANDS)]
for src, path in srcs:
    P = pages(path); B = bifolia(P); pf = Counter(w for d in P.values() for w in set(d['words'])); row = []
    for lo, hi in BANDS:
        sh = lambda x, y: len({w for w in set(P[x]['words']) & set(P[y]['words']) if lo <= pf[w] <= hi})
        d = np.array([sh(a + 'v', b + 'r') - sh(b + 'v', a + 'r') for bl in B.values() for a, b in bl])
        row.append(f'{d.mean():+.2f} (p {wilcoxon(d).pvalue:.2f}, n {len(d)})')
    L.append(f'{src} | ' + ' | '.join(row))
open(os.path.join(HERE, 'singulion_vs_nesting.txt'), 'a', encoding='utf-8').write('\n'.join(L) + '\n')
print('\n'.join(L))
