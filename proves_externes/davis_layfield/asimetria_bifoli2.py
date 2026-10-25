# Estudi crític de l'asimetria dins del bifoli (M3), 25/10/2026. Per a cada bifoli (a, b) dels quaderns A–G, M, T, els sis parells
# de pàgines, amb la distància d'escriptura si el plec s'escriu a-r, a-v, b-r, b-v: a-r|a-v (1), a-v|b-r (1, cara interior),
# b-r|b-v (1), a-r|b-r (2), a-v|b-v (2), b-v|a-r (3, cara exterior). Diverses mesures de semblança, cadascuna amb el contrast
# aparellat interior − exterior (Wilcoxon i canvi de signe), el pendent per distància, per secció i per mà, amb i sense el bifoli
# central, i amb pàgines igualades en llargada. També les quasi-bessones (A1) entre pàgines i la seva alineació vertical.
#   PYTHONIOENCODING=utf-8 py -3 proves_externes/davis_layfield/asimetria_bifoli2.py
# Entrada: escriba/manuscrit_out/{real,scribe_seed*}.txt. Sortida: aquí, asimetria2.txt i asimetria2.json
import os, re, sys, glob, json, math
import numpy as np
from collections import Counter, defaultdict
from scipy.stats import wilcoxon
HERE = os.path.dirname(os.path.abspath(__file__)); NOV = os.path.abspath(os.path.join(HERE, '..', '..'))
K = 75; CHUNK, MINREM = 40, 20
QUIRES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'M', 'T']
PAIRS = [('a-r|a-v', 1), ('a-v|b-r', 1), ('b-r|b-v', 1), ('a-r|b-r', 2), ('a-v|b-v', 2), ('b-v|a-r', 3)]
rng = np.random.default_rng(1)
ALPH = 'abcdefghiklmnopqrstvxyz'


def pages(path):
    """pàgina -> dict(Q, L, H, S, F, lines=[[mots]...])"""
    P = {}; cur = None
    for ln in open(path, encoding='utf-8'):
        if ln.startswith('#') or not ln.strip():
            continue
        m = re.match(r'^<(f\d+[rv]\d*)>\s+<!(.*)>', ln)
        if m:
            cur = m.group(1); v = dict(re.findall(r'\$(\w)=(\S+)', m.group(2))); P[cur] = dict(v, lines=[]); continue
        m = re.match(r'^<[^>]+>\s*(.*)$', ln.rstrip('\n'))
        if not m or cur is None:
            continue
        t = m.group(1).replace('<%>', '').replace('<$>', '').replace('<->', '.')
        ws = [w for w in t.split('.') if w]
        if ws:
            P[cur]['lines'].append(ws)
    for d in P.values():
        d['words'] = [w for l in d['lines'] for w in l]
    return P


def fnum(f):
    return int(re.match(r'f(\d+)', f).group(1))


def bifolis(P):
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


# ---------- mesures de semblança entre dues pàgines ----------
def lsa_vectors(P, k=K):
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
        q *= idf
        return q, (q @ Uk) / Sk
    raw, lsa = {}, {}
    for pg, d in P.items():
        raw[pg], lsa[pg] = fold(d['words'])
    return raw, lsa


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb)) if na > 0 and nb > 0 else float('nan')


def jaccard(A, B):
    A, B = set(A), set(B)
    return len(A & B) / len(A | B) if A | B else float('nan')


def habits(ws):
    """les cinc tries lliures d'una pàgina: taxes"""
    k = sum(w.count('k') for w in ws); t = sum(w.count('t') for w in ws)
    sh = sum(w.count('sh') for w in ws); ch = sum(w.count('ch') for w in ws) - sh
    q = sum(1 for w in ws if w.startswith('q')) / len(ws)
    dy = sum(1 for w in ws if w.endswith('dy')); y = sum(1 for w in ws if w.endswith('y')) - dy
    e = sum(1 for w in ws if 'e' in w) / len(ws)
    return np.array([k / (k + t) if k + t else .5, sh / (sh + ch) if sh + ch else .5, q, dy / (dy + y) if dy + y else .5, e])


_VAR = {}
def variants(w):
    if w not in _VAR:
        s = {w}
        for i in range(len(w)):
            s.add(w[:i] + w[i + 1:])
            for c in ALPH:
                s.add(w[:i] + c + w[i + 1:])
        for i in range(len(w) + 1):
            for c in ALPH:
                s.add(w[:i] + c + w[i:])
        _VAR[w] = frozenset(s)
    return _VAR[w]


def twins(dX, dY, exact=False):
    """fracció de mots (tokens) de Y amb un bessó (igual o a distància 1) entre els tipus de X; simètric: mitjana de les dues direccions"""
    def one(src, dst):
        T = set(src['words']); n = len(dst['words'])
        if exact:
            return sum(1 for w in dst['words'] if w in T) / n
        return sum(1 for w in dst['words'] if variants(w) & T) / n
    return (one(dX, dY) + one(dY, dX)) / 2


def twin_alignment(dX, dY):
    """per als bessons exactes entre X i Y: |fracció de línia a Y − fracció de línia a X| mitjana, dividida per la mateixa cosa amb
    les línies de X barrejades (20 cops). < 1 vol dir que els bessons són a la mateixa alçada de la pàgina."""
    def frac(d):
        n = len(d['lines']); out = defaultdict(list)
        for i, l in enumerate(d['lines']):
            for w in l:
                out[w].append((i + .5) / n)
        return out
    fx, fy = frac(dX), frac(dY)
    common = set(fx) & set(fy)
    obs = [abs(a - b) for w in common for a in fx[w] for b in fy[w]]
    if len(obs) < 5:
        return float('nan'), 0
    allx = [a for v in fx.values() for a in v]
    nul = []
    for _ in range(20):
        perm = rng.permutation(allx)
        it = iter(perm); fxp = {w: [next(it) for _ in v] for w, v in fx.items()}
        nul.append(np.mean([abs(a - b) for w in common for a in fxp[w] for b in fy[w]]))
    return float(np.mean(obs) / np.mean(nul)), len(obs)


def equal_len_jaccard(P, a, b, ndraw=20):
    """Jaccard amb les quatre pàgines del bifoli retallades a l'atzar a la mateixa llargada (la mínima)"""
    pgs = [a + 'r', a + 'v', b + 'r', b + 'v']
    n = min(len(P[p]['words']) for p in pgs if p in P)
    out = defaultdict(list)
    for _ in range(ndraw):
        sub = {p: list(rng.choice(P[p]['words'], n, replace=False)) for p in pgs if p in P}
        for name, d in PAIRS:
            x, y = pair_pages(a, b, name)
            if x in sub and y in sub:
                out[name].append(jaccard(sub[x], sub[y]))
    return {k: float(np.mean(v)) for k, v in out.items()}


# ---------- estadística ----------
def signflip_p(d, n=20000):
    d = np.array(d); obs = d.mean()
    flips = rng.choice([-1, 1], size=(n, len(d))) * d
    return float((np.abs(flips.mean(1)) >= abs(obs) - 1e-12).mean())


def boot_ci(v, n=4000):
    v = np.array(v); m = [rng.choice(v, len(v)).mean() for _ in range(n)]
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def contrasts(vals):
    """vals: {name -> {bif_key -> valor}}. Contrastos aparellats per bifoli."""
    def paired(x, y):
        keys = [k for k in vals[x] if k in vals[y]]
        d = [vals[x][k] - vals[y][k] for k in keys]
        if len(d) < 6:
            return None
        return dict(mean=float(np.mean(d)), n=len(d), p_wilcoxon=float(wilcoxon(d).pvalue) if any(d) else 1.0, p_signflip=signflip_p(d), frac_pos=float(np.mean(np.array(d) > 0)), ci=boot_ci(d))
    out = {'interior-exterior': paired('a-v|b-r', 'b-v|a-r')}
    # confoliate (mitjana dels dos) − diagonals (mitjana) ; diagonals − exterior ; interior − confoliate
    def mean_of(names):
        keys = set.intersection(*[set(vals[n]) for n in names])
        return {k: float(np.mean([vals[n][k] for n in names])) for k in keys}
    vals['_conf'] = mean_of(['a-r|a-v', 'b-r|b-v']); vals['_diag'] = mean_of(['a-r|b-r', 'a-v|b-v'])
    out['confoliate-diagonals'] = paired('_conf', '_diag'); out['diagonals-exterior'] = paired('_diag', 'b-v|a-r'); out['interior-confoliate'] = paired('a-v|b-r', '_conf')
    # pendent per distància dins de cada bifoli
    slopes = []
    for k in vals['a-v|b-r']:
        xs, ys = [], []
        for name, d in PAIRS:
            if k in vals[name]:
                xs.append(d); ys.append(vals[name][k])
        if len(set(xs)) == 3:
            slopes.append(float(np.polyfit(xs, ys, 1)[0]))
    out['pendent_per_distancia'] = dict(mean=float(np.mean(slopes)), n=len(slopes), p_signflip=signflip_p(slopes), frac_neg=float(np.mean(np.array(slopes) < 0)))
    return out


def analyse(path, is_real):
    P = pages(path); B = bifolis(P); raw, lsa = lsa_vectors(P)
    hand = lambda pg: P[pg].get('H', '?')
    measures = {'lsa': lambda x, y: cos(lsa[x], lsa[y]), 'tfidf': lambda x, y: cos(raw[x], raw[y]),
                'jaccard': lambda x, y: jaccard(P[x]['words'], P[y]['words']),
                'habits_dist': lambda x, y: -float(np.abs(habits(P[x]['words']) - habits(P[y]['words'])).sum()),
                'twins_ed1': lambda x, y: twins(P[x], P[y]), 'twins_exact': lambda x, y: twins(P[x], P[y], exact=True)}
    vals = {m: defaultdict(dict) for m in measures}; vals['jaccard_eqlen'] = defaultdict(dict); vals['twin_align'] = defaultdict(dict)
    meta = {}
    for q, bl in B.items():
        for i, (a, b) in enumerate(bl):
            key = f'{q}:{a}|{b}'
            meta[key] = dict(q=q, grup='herbari' if q <= 'G' else q, pos='central' if i == len(bl) - 1 else 'no central',
                             hand=Counter(hand(p) for p in (a + 'r', a + 'v', b + 'r', b + 'v') if p in P).most_common(1)[0][0],
                             n_words={p: len(P[p]['words']) for p in (a + 'r', a + 'v', b + 'r', b + 'v') if p in P})
            for name, d in PAIRS:
                x, y = pair_pages(a, b, name)
                if x in P and y in P:
                    for m, f in measures.items():
                        vals[m][name][key] = f(x, y)
                    if is_real or name in ('a-v|b-r', 'b-v|a-r', 'a-r|a-v'):
                        r, n = twin_alignment(P[x], P[y]); vals['twin_align'][name][key] = r
            for name, v in equal_len_jaccard(P, a, b).items():
                vals['jaccard_eqlen'][name][key] = v
    res = {'n_bifolis': len(meta), 'meta': meta, 'mesures': {}}
    for m in vals:
        V = {name: dict(vals[m][name]) for name, _ in PAIRS}
        if not V['a-v|b-r']:
            continue
        r = {'mitjanes': {name: float(np.nanmean(list(V[name].values()))) for name, _ in PAIRS}}
        r['contrastos'] = contrasts({k: dict(v) for k, v in V.items()})
        # per grup, per mà, sense central: només el contrast interior−exterior
        def sub(cond):
            keys = [k for k in V['a-v|b-r'] if k in V['b-v|a-r'] and cond(meta[k])]
            d = [V['a-v|b-r'][k] - V['b-v|a-r'][k] for k in keys]
            return dict(n=len(d), mean=float(np.mean(d)) if d else float('nan'), frac_pos=float(np.mean(np.array(d) > 0)) if d else float('nan'),
                        p_signflip=signflip_p(d) if len(d) >= 6 else float('nan'), interior=float(np.mean([V['a-v|b-r'][k] for k in keys])) if d else float('nan'),
                        exterior=float(np.mean([V['b-v|a-r'][k] for k in keys])) if d else float('nan'))
        r['per_grup'] = {g: sub(lambda mt, g=g: mt['grup'] == g) for g in ('herbari', 'M', 'T')}
        r['per_ma'] = {h: sub(lambda mt, h=h: mt['hand'] == h) for h in sorted({mt['hand'] for mt in meta.values()})}
        r['sense_central'] = sub(lambda mt: mt['pos'] != 'central')
        # confusor de llargada: correlació entre (interior − exterior) i la diferència de mots entre els dos parells
        keys = [k for k in V['a-v|b-r'] if k in V['b-v|a-r']]
        d = np.array([V['a-v|b-r'][k] - V['b-v|a-r'][k] for k in keys])
        dl = np.array([sum(meta[k]['n_words'].get(p, 0) for p in pair_pages(*k.split(':')[1].split('|'), 'a-v|b-r')) - sum(meta[k]['n_words'].get(p, 0) for p in pair_pages(*k.split(':')[1].split('|'), 'b-v|a-r')) for k in keys])
        r['corr_llargada'] = float(np.corrcoef(d, dl)[0, 1]) if len(d) > 3 else float('nan')
        res['mesures'][m] = r
    return res


srcs = [('real', os.path.join(NOV, 'escriba', 'manuscrit_out', 'real.txt'))] + \
       [(os.path.basename(p)[:-4], p) for p in sorted(glob.glob(os.path.join(NOV, 'escriba', 'manuscrit_out', 'scribe_seed*.txt')))]
ALL = {}
for s, p in srcs:
    ALL[s] = analyse(p, s == 'real'); print('fet', s, flush=True)
sc = [r for s, r in ALL.items() if s.startswith('scribe')]
R = ALL['real']
L = [f"Asimetria dins del bifoli, estudi crític (quaderns {' '.join(QUIRES)}, {R['n_bifolis']} bifolis; escriba = mitjana de {len(sc)} llavors)", '']
names = [n for n, _ in PAIRS]
for m in R['mesures']:
    r = R['mesures'][m]; scm = [x['mesures'][m] for x in sc if m in x['mesures']]
    L += [f'=== {m}', 'parell | real | escriba']
    for n in names:
        v = r['mitjanes'].get(n, float('nan')); e = np.mean([x['mitjanes'][n] for x in scm]) if scm else float('nan')
        L.append(f'  {n} | {v:.4f} | {e:.4f}')
    L.append('contrast aparellat | real: mitjana [IC], p Wilcoxon, p signe, % > 0 | escriba: mitjana, p signe (mín–màx)')
    for c, cv in r['contrastos'].items():
        if cv is None:
            continue
        if c == 'pendent_per_distancia':
            es = [x['contrastos'][c] for x in scm]
            L.append(f"  {c} | {cv['mean']:+.4f}, p={cv['p_signflip']:.3f}, {100*cv['frac_neg']:.0f}% negatius (n={cv['n']}) | {np.mean([e['mean'] for e in es]):+.4f}, p {min(e['p_signflip'] for e in es):.2f}–{max(e['p_signflip'] for e in es):.2f}" if es else f"  {c} | {cv['mean']:+.4f}, p={cv['p_signflip']:.3f}")
        else:
            es = [x['contrastos'][c] for x in scm if x['contrastos'].get(c)]
            L.append(f"  {c} | {cv['mean']:+.4f} [{cv['ci'][0]:+.4f}, {cv['ci'][1]:+.4f}], pW={cv['p_wilcoxon']:.3f}, pS={cv['p_signflip']:.3f}, {100*cv['frac_pos']:.0f}% (n={cv['n']})" +
                     (f" | {np.mean([e['mean'] for e in es]):+.4f}, p {min(e['p_signflip'] for e in es):.2f}–{max(e['p_signflip'] for e in es):.2f}" if es else ''))
    L.append('interior − exterior per grup / mà / sense central (real): n, interior, exterior, mitjana, % > 0, p signe')
    for g, gv in list(r['per_grup'].items()) + [('mà ' + h, hv) for h, hv in r['per_ma'].items()] + [('sense central', r['sense_central'])]:
        if gv['n']:
            L.append(f"  {g} | n={gv['n']} | {gv['interior']:.4f} / {gv['exterior']:.4f} | {gv['mean']:+.4f} | {100*gv['frac_pos']:.0f}% | p={gv['p_signflip']:.3f}")
    L.append(f"correlació de (interior − exterior) amb la diferència de mots entre els dos parells: {r['corr_llargada']:+.2f}")
    L.append('')
open(os.path.join(HERE, 'asimetria2.txt'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
json.dump(ALL, open(os.path.join(HERE, 'asimetria2.json'), 'w', encoding='utf-8'), indent=1, default=str)
print('\n'.join(L))
