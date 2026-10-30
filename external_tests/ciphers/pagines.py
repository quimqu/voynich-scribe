# El sobrant lèxic de §5, pàgina a pàgina (30/10/2026): els mots de freqüència mitjana que una pàgina fa servir més del que
# tocaria, segueixen el tema (secció, dibuix) o la mà? Tres proves, el real contra l'skribe (3 llavors):
#  A. concentració per pàgina dels mots de freqüència mitjana, dins de cada grup mà × secció (índex de dispersió);
#  B. amb qui comparteix mots clau una pàgina: mateixa secció i una altra mà, o mateixa mà i una altra secció
#     (cosinus TF-IDF dels mots de freqüència mitjana; parelles del mateix full fora, per no comptar la sessió, G6);
#  C. les etiquetes del dibuix: surten al text de la seva pàgina (igual o a un glif) més que al d'una altra pàgina de la mateixa secció?
#   py -3 pagines.py   -> pagines.json, pagines_out.txt
import os, sys, re, math, random, json
from collections import Counter, defaultdict
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); SCRIBE = (os.environ.get('SCRIBE') or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'scribe'))
sys.path.insert(0, SCRIBE); sys.path.insert(0, HERE); os.chdir(SCRIBE)
from scribe import Escriba, L_ALL
os.chdir(HERE)
import lab, mesures
from sobrant import norm

real = norm(L_ALL); info = {l['page']: (l['hand'], l['section'], l['sheet']) for l in real}
G = Counter(w for l in real for w in l['ws'])
MID = {w for w, c in G.items() if 5 <= c <= 50}     # freqüència mitjana al text sencer

def pages(L):
    P = defaultdict(Counter)
    for l in L: P[l['page']].update(l['ws'])
    return P

# ---------------- A. concentració per pàgina
def dispersion(L, minw=60):
    P = pages(L); grp = defaultdict(list)
    for p, c in P.items():
        if sum(c.values()) >= minw and p in info: grp[info[p][:2]].append(c)
    D = []
    for g, cs in grp.items():
        if len(cs) < 4: continue
        n = np.array([sum(c.values()) for c in cs], float); tot = Counter(); [tot.update(c) for c in cs]; N = n.sum()
        for w in MID:
            if tot[w] < 5: continue
            x = np.array([c[w] for c in cs], float); e = n * tot[w] / N
            D.append(((x - e) ** 2 / e).sum() / (len(cs) - 1))
    return float(np.mean(D)), float(np.median(D)), len(D)

# ---------------- B. amb qui es comparteixen els mots clau
def sharing(L, minw=60):
    P = {p: c for p, c in pages(L).items() if sum(c.values()) >= minw and p in info}
    df = Counter(w for c in P.values() for w in c if w in MID); NP = len(P)
    V = {}
    for p, c in P.items():
        v = {w: k * math.log(NP / df[w]) for w, k in c.items() if w in MID}; z = math.sqrt(sum(x * x for x in v.values())) or 1
        V[p] = {w: x / z for w, x in v.items()}
    cell = defaultdict(list); ps = list(P)
    for i, a in enumerate(ps):
        for b in ps[i + 1:]:
            ha, sa, fa = info[a]; hb, sb, fb = info[b]
            if fa == fb: continue
            cs = sum(x * V[b].get(w, 0) for w, x in V[a].items())
            k = ('mateixa mà' if ha == hb else 'altra mà') + ', ' + ('mateixa secció' if sa == sb else 'altra secció')
            cell[k].append(cs)
    return {k: float(np.mean(v)) for k, v in cell.items()}, {k: len(v) for k, v in cell.items()}

# ---------------- C. etiquetes
def labels():
    Z = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(HERE)), 'df_lines_ZL3b_strokes.csv'), dtype={'davis_hand': str}); Z = Z[Z.is_label == 1]
    out = defaultdict(list)
    for r in Z.itertuples():
        for w in re.split(r'[.#,\s]+', mesures.clean(r.text_eva_raw)):
            if len(w) >= 3 and all(c in mesures.OK for c in w): out[r.page_tag].append(w)
    return out

def label_test(L, reps=200, seed=0):
    rng = random.Random(seed); LB = labels(); P = pages(L)
    bysec = defaultdict(list)
    for p in P:
        if p in info: bysec[info[p][1]].append(p)
    def hit(w, c, exact):
        if exact: return w in c
        return any(d in VAR[p_] for d in mesures.delvars(w)) if False else bool(mesures.delvars(w) & c['__dv'])
    for p, c in P.items():
        dv = set()
        for w in c: dv |= mesures.delvars(w)
        c['__dv'] = dv
    res = {}
    for exact in (True, False):
        own = []; oth = []
        for p, ws in LB.items():
            if p not in P or p not in info: continue
            pool = [q for q in bysec[info[p][1]] if q != p and info[q][2] != info[p][2]]
            if not pool: continue
            for w in ws:
                own.append(w in P[p] if exact else bool(mesures.delvars(w) & P[p]['__dv']))
                q = [rng.choice(pool) for _ in range(reps)]
                oth.append(np.mean([(w in P[x]) if exact else bool(mesures.delvars(w) & P[x]['__dv']) for x in q]))
        res['igual' if exact else 'a un glif'] = dict(propia=float(np.mean(own)), altra=float(np.mean(oth)), n=len(own))
    for c in P.values(): c.pop('__dv', None)
    return res

if __name__ == '__main__':
    R = {}
    texts = {'real': real}
    for s in (1, 2, 3): texts[f'skribe {s}'] = norm(Escriba().write(seed=s))
    for k, L in texts.items():
        R[k] = dict(A=dispersion(L), B=sharing(L)[0], C=label_test(L)); print(k, json.dumps(R[k], ensure_ascii=False), flush=True)
    R['_n_parelles'] = sharing(real)[1]
    json.dump(R, open(os.path.join(HERE, 'pagines.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
