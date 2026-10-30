# Trios "quasi repetits" (XIFRATS.md §9): un altre trio, en una altra línia, on cada mot és igual o a una lletra de distància.
# Els textos, de frases_controls.py; a més, l'skribe amb l'hàbit de parelles de §8.   py -3 frases_quasi.py
import os
__file__ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frases_controls.py')
exec(open(__file__, encoding='utf-8').read().split("def grams")[0])
from collections import defaultdict
def dels(w): return {w[:i] + w[i + 1:] for i in range(len(w))} | {w}
def neigh(vocab):
    K = defaultdict(set)
    for w in vocab:
        for k in dels(w): K[k].add(w)
    N = {}
    for w in vocab:
        s = set()
        for k in dels(w): s |= K[k]
        N[w] = s   # superconjunt de lev<=1 (inclou alguns lev 2 per transposició; es filtra)
    return N
def lev1(a, b):
    if a == b: return True
    if abs(len(a) - len(b)) > 1: return False
    if len(a) == len(b): return sum(x != y for x, y in zip(a, b)) == 1
    if len(a) > len(b): a, b = b, a
    return any(b[:i] + b[i + 1:] == a for i in range(len(b)))
def fuzzy(L, n=3):
    T = [(li, i, tuple(l[i:i + n])) for li, l in enumerate(L) for i in range(len(l) - n + 1)]
    vocab = {w for l in L for w in l}; N = neigh(vocab); by_first = defaultdict(list)
    for t in T: by_first[t[2][0]].append(t)
    exact = Counter(t[2] for t in T); fz = 0; fz_only = 0
    for li, i, g in T:
        hit = False
        for a in N[g[0]]:
            if not lev1(a, g[0]): continue
            for lj, j, h in by_first[a]:
                if lj == li: continue
                if all(lev1(x, y) for x, y in zip(g[1:], h[1:])): hit = True; break
            if hit: break
        if hit:
            fz += 1
            if exact[g] == 1: fz_only += 1
    return len(T), fz, fz_only
for nm in list(T):
    if not any(k in nm for k in ['Voynich', 'Apicius', 'Culpeper', 'Promessi', 'Commedia', 'docta', 'homòfons', 'Naibbe', 'skribe']): continue
    n, fz, fo = fuzzy(T[nm]); print('%-48s trios %6d | amb un bessó quasi igual en una altra línia: %5d (%.1f%%) | dels quals no exactes: %5d' % (nm[:48], n, fz, 100 * fz / n, fo), flush=True)
sys.path.insert(0, HERE); import memoria_mots as MM
odd = [l for l in SC.L_ALL if SC.folio_num(l['page']) % 2]
for s in (1, 2):
    n, fz, fo = fuzzy([l['ws'] for l in MM.Memoria(MM.attraction(odd, *MM.TABLES['estreta']), 0.13).write(seed=s)])
    print('%-48s trios %6d | amb un bessó quasi igual en una altra línia: %5d (%.1f%%)' % (f'skribe + hàbit de parelles, llavor {s}', n, fz, 100 * fz / n), flush=True)
