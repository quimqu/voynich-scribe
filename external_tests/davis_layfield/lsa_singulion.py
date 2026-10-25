# Replication of Davis & Layfield, "Singulion Structure and the Voynich Manuscript" (Digital Medievalist 19, 2026): LSA on the text
# per page (documents of 40 words, TF-IDF, SVD k=75, cosine) and similarity between pairs of pages according to their physical
# relation: confoliate (recto and verso of the same folio), conjoint (inner face of the bifolium: a-v | b-r), facing (consecutive
# pages in the current order, v | r). We add the outer face of the bifolium (b-v | a-r) and the diagonals (a-r | b-r, a-v | b-v).
# The same is done on the real text and on the scribe's text (without meaning) to see whether the signal comes from production.
#   PYTHONIOENCODING=utf-8 py -3 external_tests/davis_layfield/lsa_singulion.py [--k 75] [--stop 0]
# Input: scribe/manuscript_out/{real,scribe_seed*}.txt (scribe/manuscript.py). Output: here, results_k<K>_stop<S>.{txt,json}
import os, re, sys, glob, json, math, itertools
import numpy as np
from collections import Counter, defaultdict
from scipy.stats import mannwhitneyu
HERE = os.path.dirname(os.path.abspath(__file__)); NOV = os.path.abspath(os.path.join(HERE, '..', '..'))
K = int(sys.argv[sys.argv.index('--k') + 1]) if '--k' in sys.argv else 75
STOP = int(sys.argv[sys.argv.index('--stop') + 1]) if '--stop' in sys.argv else 0
CHUNK, MINREM = 40, 20
QUIRES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'M', 'T']   # theirs: 1-7, 13, 20
TYPES = ['confoliate', 'conjoint', 'outer', 'diag', 'facing']


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


def folio(pg):
    m = re.match(r'(f\d+)([rv])', pg); return m.group(1), m.group(2)


def fnum(f):
    return int(f[1:])


def lsa(P, k, stop):
    docs = []
    for pg, d in P.items():
        ws = d['words']
        for i in range(0, len(ws), CHUNK):
            c = ws[i:i + CHUNK]
            if len(c) >= MINREM:
                docs.append(c)
    tf_all = Counter(w for c in docs for w in c)
    stopw = set(w for w, _ in tf_all.most_common(stop)) if stop else set()
    df = Counter()
    for c in docs:
        df.update(set(c))
    terms = sorted(t for t in df if df[t] >= 2 and t not in stopw); ix = {t: i for i, t in enumerate(terms)}
    N = len(docs); idf = np.array([math.log(N / df[t]) for t in terms])
    A = np.zeros((len(terms), N))
    for j, c in enumerate(docs):
        for w, n in Counter(c).items():
            if w in ix:
                A[ix[w], j] = n
    A *= idf[:, None]
    U, S, Vt = np.linalg.svd(A, full_matrices=False); Uk = U[:, :k]; Sk = S[:k]

    def fold(ws):
        q = np.zeros(len(terms))
        for w, n in Counter(ws).items():
            if w in ix:
                q[ix[w]] = n
        q *= idf
        return (q @ Uk) / Sk
    vec = {pg: fold(d['words']) for pg, d in P.items()}
    return vec, dict(terms=len(terms), docs=N)


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb)) if na > 0 and nb > 0 else float('nan')


def pairs(P):
    """pairs by type -> list of (quire, p1, p2); and bifolia per quire"""
    out = defaultdict(list); byq = defaultdict(dict)
    for pg, d in P.items():
        if d['Q'] in QUIRES and re.fullmatch(r'f\d+[rv]', pg):
            byq[d['Q']][pg] = d
    bifs = {}
    for q, pgs in byq.items():
        folios = sorted({folio(p)[0] for p in pgs}, key=fnum)
        for f in folios:
            if f + 'r' in pgs and f + 'v' in pgs:
                out['confoliate'].append((q, f + 'r', f + 'v'))
        for f1, f2 in zip(folios, folios[1:]):
            if f1 + 'v' in pgs and f2 + 'r' in pgs:
                out['facing'].append((q, f1 + 'v', f2 + 'r'))
        sheets = defaultdict(set)
        for p, d in pgs.items():
            sheets[d['F']].add(folio(p)[0])
        bl = []
        for s, fs in sheets.items():
            fs = sorted(fs, key=fnum)
            if len(fs) != 2:
                continue
            a, b = fs; bl.append((a, b))
            if a + 'v' in pgs and b + 'r' in pgs:
                out['conjoint'].append((q, a + 'v', b + 'r'))
            if b + 'v' in pgs and a + 'r' in pgs:
                out['outer'].append((q, b + 'v', a + 'r'))
            if a + 'r' in pgs and b + 'r' in pgs:
                out['diag'].append((q, a + 'r', b + 'r'))
            if a + 'v' in pgs and b + 'v' in pgs:
                out['diag'].append((q, a + 'v', b + 'v'))
        bifs[q] = sorted(bl, key=lambda ab: fnum(ab[0]))
    return out, bifs


def reorder(bifs, vec):
    """singulion sequences: each bifolium is read a-r a-v b-r b-v; facing = consecutive (v, r) pairs"""
    def score(seq):
        order = []
        for a, b in seq:
            order += [a + 'r', a + 'v', b + 'r', b + 'v']
        sc = [cos(vec[x], vec[y]) for x, y in zip(order, order[1:]) if x.endswith('v') and y.endswith('r') and x in vec and y in vec]
        return float(np.mean(sc))
    folios = sorted({f for ab in bifs for f in ab}, key=fnum)
    cur = float(np.mean([cos(vec[f1 + 'v'], vec[f2 + 'r']) for f1, f2 in zip(folios, folios[1:]) if f1 + 'v' in vec and f2 + 'r' in vec]))
    allp = sorted(((score(seq), seq) for seq in itertools.permutations(bifs)), reverse=True)
    best, bseq = allp[0]
    rank = sum(1 for s, _ in allp if s > cur) + 1
    return dict(current=cur, best=best, gain_pct=100 * (best / cur - 1), best_seq=', '.join(f'{a[1:]}|{b[1:]}' for a, b in bseq),
                rank_of_current=rank, n_perm=len(allp), median_perm=float(np.median([s for s, _ in allp])))


def analyse(path):
    P = pages(path); vec, info = lsa(P, K, STOP); pr, bifs = pairs(P)
    res = dict(space=info, types={}); vals = {}
    for t in TYPES:
        lst = pr[t]; v = [cos(vec[a], vec[b]) for q, a, b in lst]; vals[t] = v
        byq = {}
        for q in QUIRES:
            vq = [cos(vec[a], vec[b]) for qq, a, b in lst if qq == q]
            if vq:
                byq[q] = float(np.mean(vq))
        res['types'][t] = dict(mean=float(np.mean(v)), n=len(v), by_quire=byq)
    res['p'] = {f'{a}/{b}': float(mannwhitneyu(vals[a], vals[b]).pvalue) for a, b in
                [('confoliate', 'facing'), ('confoliate', 'conjoint'), ('facing', 'conjoint'), ('conjoint', 'outer'), ('confoliate', 'outer'), ('diag', 'facing')]}
    res['reorder'] = {q: reorder(bifs[q], vec) for q in ['M', 'T'] if q in bifs}
    return res


srcs = [('real', os.path.join(NOV, 'scribe', 'manuscript_out', 'real.txt'))] + \
       [(os.path.basename(p)[:-4], p) for p in sorted(glob.glob(os.path.join(NOV, 'scribe', 'manuscript_out', 'scribe_seed*.txt')))]
ALL = {}
L = [f'LSA k={K}, documents of {CHUNK} words (remainder >= {MINREM}), TF-IDF, df>=2, stop={STOP}; quires {" ".join(QUIRES)}',
     'Pair types: confoliate = r|v of the same folio · conjoint = inner face of the bifolium (a-v|b-r) · outer = outer face (b-v|a-r) · diag = a-r|b-r and a-v|b-v · facing = consecutive v|r in the current order', '',
     'source | terms/docs | confoliate | conjoint | outer | diag | facing | p conf/fac | p conf/conj | p fac/conj | p conj/outer']
for src, path in srcs:
    r = analyse(path); ALL[src] = r; t = r['types']; p = r['p']
    L.append(f"{src} | {r['space']['terms']}/{r['space']['docs']} | " + ' | '.join(f"{t[k]['mean']:.3f} (n={t[k]['n']})" for k in TYPES) +
             f" | {p['confoliate/facing']:.3f} | {p['confoliate/conjoint']:.3f} | {p['facing/conjoint']:.3f} | {p['conjoint/outer']:.3f}")
    print(L[-1], flush=True)
L += ['', 'Singulion reordering (mean facing; current = nested quire; best of all permutations of the bifolia):',
      'source | quire | current | best | gain % | rank of current | median of permutations | best sequence']
for src, r in ALL.items():
    for q, d in r['reorder'].items():
        L.append(f"{src} | {q} | {d['current']:.3f} | {d['best']:.3f} | {d['gain_pct']:.1f} | {d['rank_of_current']}/{d['n_perm']} | {d['median_perm']:.3f} | {d['best_seq']}")
L += ['', 'Per quire (confoliate / conjoint / outer / facing):']
for src, r in ALL.items():
    t = r['types']
    for q in QUIRES:
        if q in t['confoliate']['by_quire']:
            L.append(f"{src} | {q} | " + ' / '.join(f"{t[k]['by_quire'].get(q, float('nan')):.3f}" for k in ['confoliate', 'conjoint', 'outer', 'facing']))
sc = [r for s, r in ALL.items() if s.startswith('scribe')]
if sc:
    L += ['', f'Scribe, mean of {len(sc)} seeds: ' + ' · '.join(f"{k} {np.mean([r['types'][k]['mean'] for r in sc]):.3f}±{np.std([r['types'][k]['mean'] for r in sc]):.3f}" for k in TYPES),
          'Real: ' + ' · '.join(f"{k} {ALL['real']['types'][k]['mean']:.3f}" for k in TYPES)]
    for q in ['M', 'T']:
        L.append(f"  reordering {q}: scribe gain {np.mean([r['reorder'][q]['gain_pct'] for r in sc]):.1f}±{np.std([r['reorder'][q]['gain_pct'] for r in sc]):.1f}% · real {ALL['real']['reorder'][q]['gain_pct']:.1f}%")
open(os.path.join(HERE, f'results_k{K}_stop{STOP}.txt'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
json.dump(ALL, open(os.path.join(HERE, f'results_k{K}_stop{STOP}.json'), 'w', encoding='utf-8'), indent=1)
print('\n'.join(L[len(srcs) + 4:]))
