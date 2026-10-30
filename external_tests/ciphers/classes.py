# La informació d'ordre té forma de seqüència de lletres? (30/10/2026, post hoc, arran d'ordre.py)
# Agrupament de mots per intercanvi (Kneser-Ney 1993): K classes que maximitzen la informació mútua entre la classe d'un mot i
# la del següent (mateixa línia). Mots: els 600 més freqüents dels senars; la resta, una classe fixa a part. S'aprèn dels folis
# senars i es mesura als parells: MI(classe, classe següent) als parells menys la dels parells amb els mots barrejats dins de
# la línia. Un missatge de lletres (xifrat amb llatí) hauria de guanyar fins a ~20-25 classes; un text sense seqüència, gairebé res.
#   py -3 classes.py -> classes.json
import os, sys, json, math, random
from collections import Counter, defaultdict
import numpy as np
sys.argv = ['x', 'classes']
import xifrat_escriba as X, xifrat_extra as E
SC = X.SC
odd_ = lambda L: [l for l in L if SC.folio_num(l['page']) % 2]; even_ = lambda L: [l for l in L if not SC.folio_num(l['page']) % 2]


def pairs(L):
    return [(a, b) for l in L for a, b in zip(l['ws'], l['ws'][1:])]


def mi(P):
    n = len(P); xy = Counter(P); x = Counter(a for a, _ in P); y = Counter(b for _, b in P)
    return sum(v / n * math.log2(v * n / (x[a] * y[b])) for (a, b), v in xy.items())


def exchange(L, K, top=600, iters=6, seed=0):
    vocab = [w for w, _ in Counter(w for l in L for w in l['ws']).most_common(top)]; V = set(vocab)
    m = lambda w: w if w in V else '*'
    P = [(m(a), m(b)) for a, b in pairs(L)]
    rng = random.Random(seed); cls = {w: rng.randrange(K) for w in vocab}; cls['*'] = K
    right = defaultdict(Counter); left = defaultdict(Counter)
    for a, b in P: right[a][b] += 1; left[b][a] += 1
    N = len(P)
    def counts():
        cc = Counter(); cl = Counter(); cr = Counter()
        for (a, b), v in Counter(P).items(): cc[(cls[a], cls[b])] += v; cl[cls[a]] += v; cr[cls[b]] += v
        return cc, cl, cr
    def obj(cc, cl, cr):
        return sum(v * math.log(v) for v in cc.values() if v) - sum(v * math.log(v) for v in cl.values() if v) - sum(v * math.log(v) for v in cr.values() if v)
    cc, cl, cr = counts()
    for _ in range(iters):
        moved = 0
        for w in vocab:
            old = cls[w]; best = old; bestv = None
            # efecte de moure w: recalcula les files i columnes afectades (prou ràpid amb K petit)
            for k in [old] + [k for k in range(K) if k != old]:   # primer on és ara: només es mou si millora
                cls[w] = k
                d_cc = Counter(); d_l = Counter(); d_r = Counter()
                v = 0.0
                cc2 = Counter(cc)
                for b, c in right[w].items():
                    cb_old = old if b == w else cls[b]; cb_new = k if b == w else cls[b]
                    cc2[(old, cb_old)] -= c; cc2[(k, cb_new)] += c
                for a, c in left[w].items():
                    if a == w: continue
                    cc2[(cls[a], old)] -= c; cc2[(cls[a], k)] += c
                cl2 = Counter(cl); cr2 = Counter(cr); s_r = sum(right[w].values()); s_l = sum(left[w].values())
                cl2[old] -= s_r; cl2[k] += s_r; cr2[old] -= s_l; cr2[k] += s_l
                v = obj(cc2, cl2, cr2)
                if bestv is None or v > bestv + 1e-9: bestv = v; best = k; keep = (cc2, cl2, cr2)
            cls[w] = best
            if best != old: moved += 1
            cc, cl, cr = keep if best != old else counts()
        if moved == 0: break
    return cls


def heldout(cls, L, reps=5):
    m = lambda w: cls.get(w, cls['*'])
    real = mi([(m(a), m(b)) for a, b in pairs(L)])
    rng = random.Random(1); base = []
    for _ in range(reps):
        P = []
        for l in L:
            ws = l['ws'][:]; rng.shuffle(ws); P += [(m(a), m(b)) for a, b in zip(ws, ws[1:])]
        base.append(mi(P))
    return real - float(np.mean(base))


if __name__ == '__main__':
    code, us, text = X.setup(0.0)
    f = Counter(text); rnd = ''.join(random.Random(9).choices(list(f), weights=list(f.values()), k=len(text))); code_r, us_r = E.setup_text(rnd)
    texts = {'real': SC.L_ALL, 'skribe 1': SC.Escriba().write(seed=1), 'skribe 2': SC.Escriba().write(seed=2),
             'xifrat llatí 1': X.Cipher(code, us).write(seed=1), 'xifrat llatí 2': X.Cipher(code, us).write(seed=2),
             'xifrat lletres a l\'atzar 1': X.Cipher(code_r, us_r).write(seed=1)}
    R = {}
    for nm, L in texts.items():
        R[nm] = {}
        for K in (2, 4, 8, 16, 24, 32):
            cls = exchange(odd_(L), K); R[nm][K] = heldout(cls, even_(L))
        print(f'{nm:30}', ' '.join(f'K={k}:{v:.4f}' for k, v in R[nm].items()), flush=True)
    json.dump(R, open(os.path.join(X.HERE, 'classes.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
