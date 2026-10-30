# Parelles, trios i quatriots de mots (30/10/2026, arran de §8 de XIFRATS.md): seqüències de 2, 3 i 4 mots seguits de la mateixa
# línia que el Voynich real escriu més sovint del que tocaria si els mots de cada línia fossin en qualsevol ordre.
#  - esperat = mitjana de N barreges dels mots dins de cada línia (es manté què hi ha a cada línia; només canvia l'ordre);
#  - parelles: descoberta als folis SENARS, confirmació als PARELLS (la mateixa seqüència, per sobre de l'atzar a l'altra meitat);
#    trios i quatriots: són tan rars que es miren al text sencer (els que surten 2 cops o més), i es diu si surten a totes dues meitats;
#  - controls: quantes seqüències es repeteixen al llatí (De docta ignorantia a la mateixa maqueta), a l'skribe i a l'skribe amb
#    l'hàbit de parelles de §8 (memoria_mots.py);
#  - per als trios i quatriots, «més enllà de les parelles»: comptatge real contra el que donaria una cadena de parelles
#    (c(ABC) contra c(AB)·c(BC)/c(B)): si el trio és una unitat o només la suma de dues parelles atretes;
#  - el mateix a l'skribe (98ecf31, 3 llavors), que no té memòria de mot a mot: si hi surt, ho fa el procediment (còpia, contacte);
#  - sense les seqüències amb mots iguals o a un glif seguits (això és la còpia de l'skribe), que es compten a part.
#   py -3 ngrames.py [barreges=300]  -> ngrames.txt, ngrames.json
import os, sys, json, math, random
from collections import Counter, defaultdict
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIBE = (os.environ.get('SCRIBE') or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'scribe'))
sys.path.insert(0, SCRIBE); os.chdir(SCRIBE)
import scribe as SC
os.chdir(HERE); sys.stdout.reconfigure(encoding='utf-8')
REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 300
odd_ = lambda L: [l for l in L if SC.folio_num(l['page']) % 2]; even_ = lambda L: [l for l in L if not SC.folio_num(l['page']) % 2]
near = lambda a, b: a == b or SC.M.lev(a, b) <= 1
copy_like = lambda g: any(near(a, b) for a, b in zip(g, g[1:]))


def grams(L, n): return Counter(tuple(l['ws'][i:i + n]) for l in L for i in range(len(l['ws']) - n + 1))


def null(L, n, keys, reps, seed=0):
    """comptatge de cada seqüència de keys en reps barreges dins de la línia: (mitjana, fracció de barreges >= observat)"""
    rng = random.Random(seed); keys = set(keys); S = defaultdict(list)
    for _ in range(reps):
        c = Counter()
        for l in L:
            ws = l['ws'][:]; rng.shuffle(ws)
            for i in range(len(ws) - n + 1):
                g = tuple(ws[i:i + n])
                if g in keys: c[g] += 1
        for g in keys: S[g].append(c[g])
    return S


def test(L, n, cand, reps, seed=0):
    obs = grams(L, n); S = null(L, n, cand, reps, seed)
    return {g: (obs[g], float(np.mean(S[g])), (1 + sum(x >= obs[g] for x in S[g])) / (reps + 1)) for g in cand}


def chain(L, g):
    """el que esperaria una cadena de parelles: c(AB)·c(BC)/c(B) (trios) o c(ABC)·c(BCD)/c(BC) (quatriots)"""
    n = len(g); c_n1 = grams(L, n - 1); c_n2 = grams(L, n - 2) if n > 2 else None
    num = c_n1[g[:-1]] * c_n1[g[1:]]; den = c_n2[g[1:-1]] if n > 3 else Counter(w for l in L for w in l['ws'])[g[1]]
    return num / den if den else float('nan')


real = SC.L_ALL; O, E = odd_(real), even_(real)
meta = defaultdict(lambda: Counter())
for l in real:
    for n in (2, 3, 4):
        for i in range(len(l['ws']) - n + 1): meta[tuple(l['ws'][i:i + n])][(l['hand'], l['section'])] += 1
pages = defaultdict(set)
for l in real:
    for n in (2, 3, 4):
        for i in range(len(l['ws']) - n + 1): pages[tuple(l['ws'][i:i + n])].add(l['page'])
skribes = [SC.Escriba().write(seed=s) for s in (1, 2, 3)]
MIN = {2: 4, 3: 2, 4: 2}            # mínim de cops per ser candidata (parelles: als senars; trios i quatriots: al text sencer)
R = {}; out = []
say = lambda s='': (out.append(s), print(s, flush=True))
import lab, memoria_mots as MM
latin = lab.latin_lines(); memo = MM.Memoria(MM.attraction(odd_(real), *MM.TABLES['estreta']), 0.13).write(seed=1)
say(f'Seqüències de mots seguits a la mateixa línia, Voynich real (ZL3b, text de paràgraf, {sum(len(l["ws"]) for l in real)} mots).' + chr(10))
say('Quantes seqüències diferents surten 2 cops o més (i 3 o més), a la mateixa línia:')
say('%-34s' % 'text' + ''.join('%14s' % f'{n} mots' for n in (2, 3, 4, 5)))
for nm, L in [('Voynich real', real), ('llatí (De docta, mateixa maqueta)', latin)] + [(f'skribe, llavor {k + 1}', s_) for k, s_ in enumerate(skribes)] + [('skribe + hàbit de parelles (§8)', memo)]:
    cs = [grams(L, n) for n in (2, 3, 4, 5)]
    say('%-34s' % nm + ''.join('%14s' % f'{sum(v >= 2 for v in c.values())} ({sum(v >= 3 for v in c.values())})' for c in cs))
say()
say(f'Esperat = mitjana de {REPS} barreges dins de cada línia. x = observat / esperat.')
say('Parelles: descoberta als folis senars (p <= 0,01), confirmació als parells (p <= 0,05). Trios i quatriots: text sencer, p <= 0,01.')
say('«cadena» = observat / el que donarien les parelles soles (> 1: la seqüència és més que dues parelles encadenades).')
say("skribe = observat / esperat a l'skribe (3 llavors juntes), que no té memòria de mot a mot." + chr(10))
for n in (2, 3, 4):
    if n == 2:
        cO = grams(O, n); cand = [g for g, c in cO.items() if c >= MIN[n]]
        tO = test(O, n, cand, REPS, 1); disc = [g for g in cand if tO[g][2] <= 0.01 and tO[g][0] > tO[g][1]]
        tE = test(E, n, disc, REPS, 2)
    else:
        cA = grams(real, n); cand = [g for g, c in cA.items() if c >= MIN[n]]
        tA0 = test(real, n, cand, REPS, 1); disc = [g for g in cand if tA0[g][2] <= 0.01 and tA0[g][0] > tA0[g][1]]
        gO, gE = grams(O, n), grams(E, n); tE = {g: (gE[g], float('nan'), float('nan')) for g in disc}
    tA = test(real, n, disc, REPS, 3)
    tS = [test(s_, n, disc, max(50, REPS // 3), 4 + k) for k, s_ in enumerate(skribes)]
    rows = []
    for g in disc:
        o, e, p = tA[g]; oe, ee, pe = tE[g]
        so = sum(t[g][0] for t in tS); se = sum(t[g][1] for t in tS)
        top = meta[g].most_common(1)[0]
        conf = bool(pe <= 0.05 and oe > ee) if n == 2 else bool(gO[g] and gE[g])
        rows.append(dict(seq=' '.join(g), n=n, total=o, esperat=e, x=o / max(e, 1e-9), p=p, parells=oe, parells_esperat=ee, p_parells=pe,
                         confirmada=conf, cadena=(o / chain(real, g)) if n > 2 else None, copia=copy_like(g),
                         skribe=so / max(se, 1e-9) if se > 0 else (float('inf') if so else None), skribe_n=so, pagines=len(pages[g]),
                         on=f'mà {top[0][0]} {top[0][1]} {top[1]}/{o}'))
    R[n] = rows
    name = {2: 'PARELLES', 3: 'TRIOS', 4: 'QUATRIOTS'}[n]
    conf = [r for r in rows if r['confirmada']]
    if n == 2:
        say(f"== {name}: {len(cand)} candidates (4 cops o més als senars), {len(disc)} per sobre de l'atzar als senars, {len(conf)} confirmades als parells "
            f'({sum(r["copia"] for r in conf)} amb mots iguals o a un glif seguits) ==')
        show = sorted(conf, key=lambda r: (r['copia'], -r['x'] * math.log(1 + r['total'])))[:45]
    else:
        say(f"== {name}: {len(cand)} es repeteixen (2 cops o més), {len(disc)} per sobre de l'atzar, {len(conf)} a totes dues meitats; "
            f'{sum(r["copia"] for r in rows)} amb mots iguals o a un glif seguits ==')
        show = sorted(rows, key=lambda r: (r['copia'], -r['total'], -r['x']))
    for r in show:
        sk = '—' if r['skribe'] is None else ('∞' if r['skribe'] == float('inf') else f"{r['skribe']:.1f}")
        cad = '' if r['cadena'] is None else f"  cadena {r['cadena']:.1f}"
        half = f"parells {r['parells']} (esp {r['parells_esperat']:.1f})" if n == 2 else ('totes dues meitats' if r['confirmada'] else 'una meitat')
        say(f"  {'(còpia) ' if r['copia'] else ''}{r['seq']:34} {r['total']:3d} cops (esperat {r['esperat']:.2f}, x{r['x']:.0f}) · {half}{cad} · "
            f"skribe x{sk} ({r['skribe_n']}) · {r['pagines']} pàg · {r['on']}")
    say()
json.dump({str(k): v for k, v in R.items()}, open(os.path.join(HERE, 'ngrames.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
open(os.path.join(HERE, 'ngrames.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
