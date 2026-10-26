# Do two text-based reconstructions of the bifolio order agree with each other even when there is no order to recover?
# Mauro (voynich.ninja, 27/10/2026): npcompl33t's seriation agrees with the Layfield-Davis order of quires 13 and 20, which at face
# value has odds of 1/720 and 1/120. If both methods read the same signal (which pages look alike), they should agree on the skribe
# too, whose sheets have no order (each sheet draws its habits independently).
#   LD   : Layfield-Davis, as in davis_layfield/bifolium_asymmetry.py: LSA (k 75), the permutation of the bifolia that maximises
#          the mean cosine at the junctions b_i-v | a_i+1-r.
#   NPJ  : the same search with npcompl33t's similarity (minus his weighted Jensen-Shannon dissimilarity of glyph transitions).
#   NPM  : npcompl33t's seriation proper: the bifolia ordered by the mean MDS1 position of their pages (direction is arbitrary, so
#          its agreement is taken in absolute value).
# Agreement: Kendall tau between the positions of the bifolia in the two orders, per quire, and exact matches. Null: the same
# statistic for a random order against a random order (exact, by enumerating permutations).
#   PYTHONIOENCODING=utf-8 py -3 external_tests/npcompl33t/order_agreement.py
import os, glob, itertools, math
import numpy as np
from scipy.stats import kendalltau
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
DL = os.path.join(ROOT, 'external_tests', 'davis_layfield')
ns_s = {'__file__': os.path.join(HERE, 'seriation.py')}
exec(open(os.path.join(HERE, 'seriation.py'), encoding='utf-8').read().split('srcs = [')[0], ns_s)
ns_l = {'__file__': os.path.join(DL, 'bifolium_asymmetry.py')}
exec(open(os.path.join(DL, 'bifolium_asymmetry.py'), encoding='utf-8').read().split('srcs = [')[0], ns_l)
QUIRES = ns_l['QUIRES']
OUT = []


def say(s=''):
    OUT.append(s); print(s, flush=True)


def best_order(bl, sim):
    def junc(seq):
        s = [sim(x[1] + 'v', y[0] + 'r') for x, y in zip(seq, seq[1:])]
        s = [v for v in s if v is not None and not math.isnan(v)]
        return float(np.mean(s)) if s else -1e9
    return max(itertools.permutations(bl), key=junc)


def ranks(order, bl):
    return [list(order).index(b) for b in bl]


def null_tau(n, absolute):
    base = list(range(n)); v = [kendalltau(base, p).statistic for p in itertools.permutations(base)]
    v = np.abs(v) if absolute else np.array(v)
    return float(np.mean(v)), v


def analyse(path):
    P = ns_l['pages'](path); vec = ns_l['lsa'](P, ns_l['K']); B = ns_l['bifolis'](P)
    S = ns_s['read'](path); T = {pg: ns_s['transitions'](d['lines'])[0] for pg, d in S.items()}
    mds = ns_s['analyse'](path); x1 = dict(zip(mds['pages'], mds['X'][:, 0]))

    def s_lsa(a, b):
        return ns_l['cos'](vec[a], vec[b]) if a in vec and b in vec else None

    def s_js(a, b):
        return -ns_s['dissimilarity'](T[a], T[b]) if a in T and b in T and T[a] and T[b] else None
    res = {}
    for q in QUIRES:
        bl = B.get(q)
        if not bl or len(bl) < 3:
            continue
        ld = best_order(bl, s_lsa); npj = best_order(bl, s_js)
        pos = {ab: np.mean([x1[f + s] for f in ab for s in 'rv' if f + s in x1] or [np.nan]) for ab in bl}
        npm = sorted(bl, key=lambda ab: pos[ab]) if not any(np.isnan(v) for v in pos.values()) else None
        r_ld, r_npj = ranks(ld, bl), ranks(npj, bl)
        res[q] = dict(n=len(bl), ld=ld, npj=npj, npm=npm,
                      tau_npj=float(kendalltau(r_ld, r_npj).statistic), exact_npj=ld == npj,
                      tau_npm=float(abs(kendalltau(r_ld, ranks(npm, bl)).statistic)) if npm else None,
                      exact_npm=(list(ld) == npm or list(ld) == npm[::-1]) if npm else None)
    return res


srcs = [('real', os.path.join(ROOT, 'scribe', 'manuscript_out', 'real.txt'))] + \
       [(os.path.basename(p)[:-4], p) for p in sorted(glob.glob(os.path.join(ROOT, 'scribe', 'manuscript_out', 'scribe_seed*.txt')))]
R = {s: analyse(p) for s, p in srcs}
fmt = lambda seq: ' '.join(f'{a[1:]}/{b[1:]}' for a, b in seq) if seq else '-'
say('Agreement between two text-based orders of the bifolia in each quire: Layfield-Davis (LSA, best junctions) against')
say("npcompl33t's similarity (NPJ: same search with his Jensen-Shannon; NPM: his MDS1 order, |tau|). The skribe's sheets have no order.")
say('')
for s, r in R.items():
    say(f'## {s}')
    for q, d in r.items():
        say(f"  {q} ({d['n']} bifolia)  LD: {fmt(d['ld'])}")
        say(f"  {'':16}NPJ: {fmt(d['npj'])}   tau {d['tau_npj']:+.2f}{'  EXACT' if d['exact_npj'] else ''}")
        say(f"  {'':16}NPM: {fmt(d['npm'])}   |tau| {d['tau_npm']:.2f}{'  EXACT (or reversed)' if d['exact_npm'] else ''}" if d['npm'] else f"  {'':16}NPM: -")
say('')
say('Summary: mean tau over the quires (null: random against random, exact), exact matches, and the expected number of exact matches.')
say(f"{'text':14} {'NPJ tau':>8} {'null':>6} {'exact':>6} {'expected':>8}   {'NPM |tau|':>9} {'null':>6} {'exact':>6} {'expected':>8}")
for s, r in R.items():
    qs = list(r.values())
    t1 = np.mean([d['tau_npj'] for d in qs]); n1 = np.mean([null_tau(d['n'], False)[0] for d in qs])
    e1 = sum(d['exact_npj'] for d in qs); x1 = sum(1 / math.factorial(d['n']) for d in qs)
    q2 = [d for d in qs if d['npm']]
    t2 = np.mean([d['tau_npm'] for d in q2]); n2 = np.mean([null_tau(d['n'], True)[0] for d in q2])
    e2 = sum(d['exact_npm'] for d in q2); x2 = sum(2 / math.factorial(d['n']) for d in q2)
    say(f"{s:14} {t1:+8.2f} {n1:+6.2f} {e1:6d} {x1:8.2f}   {t2:9.2f} {n2:6.2f} {e2:6d} {x2:8.2f}")
# p of the mean tau against the null, by simulation (independent random orders per quire)
rng = np.random.default_rng(0)
say('')
say('p (one-sided) of the mean NPJ tau over the quires against random orders, 20,000 draws:')
for s, r in R.items():
    qs = list(r.values()); obs = np.mean([d['tau_npj'] for d in qs])
    nulls = {d['n']: null_tau(d['n'], False)[1] for d in qs}
    sim = np.mean([rng.choice(nulls[d['n']], 20000) for d in qs], axis=0)
    say(f"  {s:14} mean tau {obs:+.2f}  p {np.mean(sim >= obs - 1e-12):.4f}")
open(os.path.join(HERE, 'order_agreement.txt'), 'w', encoding='utf-8').write('\n'.join(OUT) + '\n')
