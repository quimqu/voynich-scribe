# Famílies de xifrat llatí -> voynichès. Cada funció rep mots llatins (i el Voynich de referència) i torna
# (mots xifrats, bits de nota lateral per mot que cal per desxifrar, descripció).
import io, math, random, heapq, contextlib
from collections import Counter, defaultdict
import numpy as np
import pm_cipher_nb as nb


def _H(c):
    n = sum(c.values()); return -sum(v / n * math.log2(v / n) for v in c.values()) if n else 0.0


# ---------------------------------------------------------------- C1: el PM-Cipher del notebook, tal qual
def pm_cipher(lat, voy, seed=42, sweep=True):
    nb.set_globals(voy, seed)
    with contextlib.redirect_stdout(io.StringIO()):
        best = nb.search_parameters_extended(lat, target_collision_grid=range(1, 3), trials_per=2, target_H2=nb.voy_H[1],
                                             w_H=1.0, w_jsd=2.0, use_ngrams_options=(False,))
        if sweep:
            best = nb.run_gamma_sweep_until_convergence(best, lat, voy, gamma_grid=(1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0),
                                                        tau_grid=(0.2, 0.5, 1.0), h2_target=nb.voy_H[1], h2_tol=0.20,
                                                        max_rounds=8, min_delta=5e-4, patience=1, base_seed=123, verbose=False)
    c, cw, rs = best['cipher'], best['cipher_words'], best['residuals']
    # bits de residu: H(R | posició, glif), la comptabilitat «always-send» de la cel·la 25 del notebook
    cond = defaultdict(Counter)
    for w, r in zip(cw, rs):
        for pos, (g, x) in enumerate(zip(w, r)): cond[(pos, g)][x] += 1
    nsym = sum(len(w) for w in cw)
    bits_glyph = sum(sum(cn.values()) / nsym * _H(cn) for cn in cond.values())
    # el flux conjunt (glif, residu) és una recodificació invertible del llatí: on ha anat la informació
    sym = {}
    joint = [''.join(sym.setdefault((g, x), chr(0x4E00 + len(sym))) for g, x in zip(w, r)) for w, r in zip(cw, rs)]
    return cw, bits_glyph * nsym / len(cw), dict(C=best['C'], H=best['H'], jsd=best['jsd'], bits_glyph=bits_glyph, joint=joint)


# ---------------------------------------------------------------- C2: el «homofònic» de juny de 2025 (lletra + dígit a l'atzar)
def digit_homophonic(lat, k=3, seed=1):
    r = random.Random(seed)
    return [''.join(ch + str(r.randrange(k)) for ch in w) for w in lat], 0.0, {}


# ---------------------------------------------------------------- repartiment d'homòfons per massa
def allocate(units, voy_types, seed=0):
    """Reparteix tipus de mot del Voynich entre unitats de text pla perquè la massa de cada unitat (freq. al llatí)
    quedi coberta per homòfons de massa semblant al Voynich. Torna {unitat: [(mot, pes)]}. Cada mot va a una sola unitat."""
    tot_u = sum(units.values()); tot_v = sum(voy_types.values())
    heap = [(-f / tot_u, u) for u, f in units.items()]; heapq.heapify(heap)
    table = defaultdict(list)
    vt = sorted(voy_types.items(), key=lambda x: -x[1])
    for w, f in vt:
        d, u = heapq.heappop(heap)
        table[u].append((w, f))
        heapq.heappush(heap, (d + f / tot_v, u))
    # unitats sense cap homòfon (n'hi ha més que tipus de mot): queden fora i ho diem
    missing = [u for u in units if u not in table]
    return table, missing


# ---------------------------------------------------------------- C3: tipus Naibbe (unitats d'1-2 lletres -> un mot del Voynich)
def naibbe_like(lat, voy, n_out, p_bigram=0.5, seed=2):
    r = random.Random(seed)
    stream = ''.join(lat)
    units = []; i = 0
    while i < len(stream) and len(units) < n_out:
        L = 2 if (r.random() < p_bigram and i + 1 < len(stream)) else 1
        units.append(stream[i:i + L]); i += L
    table, missing = allocate(Counter(units), Counter(voy), seed)
    out = []
    for u in units:
        hs = table.get(u)
        if not hs:   # unitat sense homòfon: es parteix en lletres (sempre en tenen)
            out.extend(r.choices([w for w, _ in table[c]], [f for _, f in table[c]])[0] for c in u); continue
        out.append(r.choices([w for w, _ in hs], [f for _, f in hs])[0])
    return out[:n_out], 0.0, dict(letters_per_word=i / max(1, len(units)), n_units=len(Counter(units)), missing=len(missing),
                                  latin_words_used=round(i / (sum(map(len, lat)) / len(lat))))


# ---------------------------------------------------------------- C4: nomenclàtor (mot llatí -> mot del Voynich pel rang)
def _extra_words(voy, need, seed=3):
    """Mots nous de forma voynichesca (model de caràcters d'ordre 3 dins del mot) per quan falten paraules de codi."""
    r = random.Random(seed); ctx = defaultdict(Counter); have = set(voy); out = []
    for w in voy:
        s = '^^' + w + '$'
        for i in range(2, len(s)): ctx[s[i - 2:i]][s[i]] += 1
    while len(out) < need:
        h = '^^'; w = ''
        while True:
            c = ctx[h]; ch = r.choices(list(c), list(c.values()))[0]
            if ch == '$' or len(w) > 12: break
            w += ch; h = h[1] + ch
        if w and w not in have: have.add(w); out.append(w)
    return out


def nomenclator(lat, voy):
    cl = Counter(lat); cv = Counter(voy)
    lt = [w for w, _ in cl.most_common()]; vt = [w for w, _ in cv.most_common()]
    vt += _extra_words(voy, max(0, len(lt) - len(vt)))
    code = dict(zip(lt, vt))
    return [code[w] for w in lat], 0.0, dict(latin_types=len(lt), voynich_types=len(cv))


# ---------------------------------------------------------------- C5: nomenclàtor amb homòfons i regla de contacte
def nomenclator_homophones(lat, voy, contact=True, seed=4):
    """Cada mot llatí té un joc d'homòfons (mots del Voynich repartits per massa). Si contact=True, l'homòfon es tria
    segons l'últim glif del mot anterior (el que el Voynich hi posaria més sovint): determinista, i es desxifra igual,
    perquè cada mot del Voynich pertany a un sol mot llatí."""
    r = random.Random(seed); cl = Counter(lat); cv = Counter(voy)
    table, missing = allocate(cl, cv, seed)
    if missing:
        extra = _extra_words(voy, len(missing))
        for u, w in zip(missing, extra): table[u] = [(w, 1)]
    # P(primer glif | últim glif anterior) al Voynich real
    trans = defaultdict(Counter)
    for a, b in zip(voy, voy[1:]): trans[a[-1]][b[0]] += 1
    out = []; prev = None
    for w in lat:
        hs = table[w]
        if contact and prev is not None and len(hs) > 1:
            t = trans[prev[-1]]; tot = sum(t.values()) or 1
            # pes = freq. de l'homòfon × afinitat de contacte; s'agafa el millor (determinista)
            c = max(hs, key=lambda x: x[1] * (t[x[0][0]] + 1) / tot)[0]
        else:
            c = r.choices([x for x, _ in hs], [f for _, f in hs])[0]
        out.append(c); prev = c
    side = 0.0
    return out, side, dict(latin_types=len(cl), with_homophones=sum(len(v) > 1 for v in table.values()), synthetic=len(missing))
