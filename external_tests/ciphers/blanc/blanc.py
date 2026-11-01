# Un missatge «blanquejat» dins de l'skribe (31/10/2026; preregistre a BLANC_PREREG.md). El llatí de §7 (lletres i espai, 27
# símbols) passa per una clau tan llarga com el text, u -> (u + k_i) mod 27, que n'esborra l'ordre (com un text comprimit o una
# taula que gira). Després, el xifrat de dues capes de §7 (xifrat_escriba.py) tal qual.
#  B1: el missatge blanquejat sol, un símbol per mot.
#  B2: el missatge blanquejat + l'hàbit de parelles de §8 (memoria_mots.py, taula estreta, λ = 0,13). Un mot que fa parella apresa
#      amb l'anterior de la línia és nul: el lector se'l salta. L'hàbit escriu nul·les; els mots de missatge no poden fer parella.
#   py -3 blanc.py prova <b1|b2>
#   py -3 blanc.py corre <tots|senars> <b1|b2> <llavor>  -> out/<tots|senars>_<b1|b2>_<llavor>.json (+ el text, _text.json)
#   py -3 blanc.py agrega                                -> blanc.txt, blanc.json (C1-C4 del preregistre)
import os, sys, json, math, random, time, inspect, textwrap
import numpy as np
from collections import Counter, defaultdict      # els fan servir pairs(), exchange() i heldout() de classes.py
HERE = os.path.dirname(os.path.abspath(__file__)); XIF = os.path.dirname(HERE)
sys.path.insert(0, XIF)
import xifrat_escriba as X              # llegeix sys.argv[2] == 'senars' per aprendre només dels senars
SC = X.SC; M = SC.M
src = open(os.path.join(XIF, 'classes.py'), encoding='utf-8').read()
exec(src[src.index('def pairs('):src.index("if __name__")])          # pairs, mi, exchange, heldout de classes.py, tal qual
src = open(os.path.join(XIF, 'memoria_mots.py'), encoding='utf-8').read()
exec(src[src.index('def near('):src.index('def order(')])            # near, attraction de memoria_mots.py, tal qual
sys.path.insert(0, os.path.join(X.lab.NOV, 'escriba', 'controls')); import control
odd_ = lambda L: [l for l in L if SC.folio_num(l['page']) % 2]; even_ = lambda L: [l for l in L if not SC.folio_num(l['page']) % 2]
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
LAM = 0.13; KEY_SEED = 7
LAM_B4 = 0.20   # B4, exploratòria: λ intermèdia, per portar l'ordre total al del real
LAM_B3 = 0.30   # B3, exploratòria (no preregistrada): B2 amb l'hàbit més fort, perquè a B2 l'hàbit només actua en un 2,7% dels mots
ALPHA = 'abcdefghijklmnopqrstuvwxyz '


def whiten(text, seed=KEY_SEED):
    r = random.Random(seed); n = len(ALPHA)
    return [ALPHA[(ALPHA.index(c) + r.randrange(n)) % n] for c in text]


def unwhiten(us, seed=KEY_SEED):
    r = random.Random(seed); n = len(ALPHA)
    return ''.join(ALPHA[(ALPHA.index(c) - r.randrange(n)) % n] for c in us)


def setup():
    lat = X.lab.words(X.lab.latin_lines()); text = ' '.join(lat)
    assert set(text) <= set(ALPHA), set(text) - set(ALPHA)
    us = whiten(text); rw = [w for l in SC.L_ALL for w in l['ws']]; code = X.Code(Counter(us), rw)
    assert not code.missing, code.missing
    return code, us, text


# ---------------- B2: com xifrat_escriba.py, però accept() sap el mot anterior de la línia (ws) per a l'hàbit i les nul·les
def _patched_write():
    s = textwrap.dedent(inspect.getsource(SC.Escriba.write)).split('\n')
    i0 = next(i for i, x in enumerate(s) if x.strip() == "for i in range(len(l['ws'])):")
    i1 = next(i for i, x in enumerate(s) if x.strip().startswith("ws.append(w); page_words.append((w,li,i))"))
    ind = ' ' * (len(s[i0 + 1]) - len(s[i0 + 1].lstrip()))
    body = ['    ' + x if x.strip() else x for x in s[i0 + 1:i1]]
    new = s[:i0 + 1] + [ind + 'self._start(ws)', ind + 'for _t in range(self.max_tries):'] + body + \
          [ind + '    if self.accept(w): break', ind + 'else:', ind + '    w=self.fallback()'] + s[i1:]
    ns = dict(SC.__dict__); exec('\n'.join(new), ns); return ns['write']


class Habit(X.Cipher):
    write = _patched_write()

    # La regla de nul·les mira les formes normalitzades (X.norm): l'skribe tanca el mot d'abans d'un buit de dibuix quan la línia ja
    # és escrita (chol -> choly), i amb les formes tal qual el lector no veia la parella que havia vist l'escrivà (31/10).
    def __init__(self, code, units, nxt, lam, **kw):
        super().__init__(code, units, **kw); self.nxt, self.lam = nxt, lam; self.nulls = 0; self.nn = null_table(nxt)

    def _start(self, ws):
        self.prev = ws[-1] if ws else None; follow = self.nxt.get(self.prev, set())
        self.want = follow if follow and self.rng.random() < self.lam else None
        self.ban = self.nn.get(X.norm(self.prev), set()) if self.prev else set()

    def accept(self, w, page_words=None):
        self.tries += 1
        if self.want is not None:
            if w in self.want: self.nulls += 1; return True
            return False
        if X.norm(w) not in self.ban and self.code.of(w) == self._target(): self.pos += 1; return True
        return False

    def fallback(self):
        self.fb += 1
        if self.want is not None: self.nulls += 1; return self.rng.choice(sorted(self.want))
        c = {w: k for w, k in self.code.words.get(self._target()).items() if X.norm(w) not in self.ban}; self.pos += 1
        return self.rng.choices(list(c), weights=list(c.values()))[0]


def null_table(nxt):
    nn = defaultdict(set)
    for a, bs in nxt.items(): nn[X.norm(a)] |= {X.norm(b) for b in bs}
    return dict(nn)


def decode(code, L, nxt=None):
    nn = null_table(nxt) if nxt else {}; out = []
    for l in L:
        prev = None
        for w in l['ws']:
            if not (prev is not None and X.norm(w) in nn.get(X.norm(prev), ())): out.append(code.of(w))
            prev = w
    return out


def grams_repeated(L, n):
    c = Counter(tuple(l['ws'][i:i + n]) for l in L for i in range(len(l['ws']) - n + 1))
    return sum(1 for v in c.values() if v >= 2)


def make(var, code, us, max_tries=400):
    if var == 'b1': return X.Cipher(code, us, max_tries=max_tries), None
    nxt = attraction(odd_(SC.L_ALL), 3, 1.0)                           # la taula «estreta» de §8: >= 3 cops, PMI >= 1 bit
    return Habit(code, us, nxt, {'b3': LAM_B3, 'b4': LAM_B4}.get(var, LAM), max_tries=max_tries), nxt


def run(split, var, seed):
    code, us, text = setup()
    lay = [l for l in SC.L_ALL if SC.folio_num(l['page']) % 2 == 0] if split == 'senars' else None
    hand = {l['page']: l['hand'] for l in SC.L_ALL}
    g, nxt = make(var, code, us); t = time.time(); out = g.write(seed=seed, layout=lay)
    for o in out: o['hand'] = hand[o['page']]
    n = sum(len(o['ws']) for o in out)
    json.dump([dict(page=o['page'], ws=o['ws']) for o in out], open(os.path.join(OUT, f'{split}_{var}_{seed}_text.json'), 'w', encoding='utf-8'))
    R = M.evaluate(out, seed=seed)
    dec = decode(code, out, nxt); lpw = len(text) / len(text.split())   # lletres (amb l'espai) per mot llatí
    info = dict(var=var, split=split, seed=seed, segons=time.time() - t, mots=n, intents=g.tries / n, reserva=g.fb, unitats=g.pos,
                nulles=getattr(g, 'nulls', 0) / n, bits_per_mot=g.pos * math.log2(len(ALPHA)) / n, mots_llatins=g.pos / lpw,
                desxifrat_ok=(dec == us[:g.pos]), llati_ok=(unwhiten(dec) == text[:g.pos]),
                tipus=len(set(w for l in out for w in l['ws'])), ordre=control.word_order(out),
                repeticio_immediata=sum(a == b for l in out for a, b in zip(l['ws'], l['ws'][1:])) / n)
    if split == 'tots':
        info['classes_K'] = {K: heldout(exchange(odd_(out), K), even_(out)) for K in (2, 4, 8, 16, 32)}
        info['repetits'] = {n_: grams_repeated(out, n_) for n_ in (2, 3, 4, 5)}
    json.dump(dict(R={k: float(v) for k, v in R.items()}, info=info), open(os.path.join(OUT, f'{split}_{var}_{seed}.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1, default=float)
    print(split, var, seed, info, flush=True)


def agrega():
    import glob
    real = SC.L_ALL; even = even_(real)
    REF = {'tots': M.evaluate(real, seed=1), 'senars': M.evaluate(even, seed=1)}
    lines = [f'Voynich real: ordre 0.088, K=2 0.012, K=32 0.054, repetits 2/3/4/5 mots { {n_: grams_repeated(real, n_) for n_ in (2, 3, 4, 5)} }']
    res = {}
    g = lambda d, k: d[str(k)] if str(k) in d else d[k]
    for var in ('b1', 'b2', 'b3', 'b4'):
        r = {}
        for split in ('tots', 'senars'):
            fs = sorted(glob.glob(os.path.join(OUT, f'{split}_{var}_[0-9].json')))
            if not fs: continue
            J = [json.load(open(f, encoding='utf-8')) for f in fs]
            G = {k: float(np.mean([j['R'][k] for j in J])) for k in J[0]['R']}
            ok = M.compare(REF[split], G)
            r[split] = dict(score=int(sum(ok.values())), falla=[k for k in ok if not ok[k]], llavors=len(J), info=[j['info'] for j in J])
        if 'tots' not in r: continue
        I = r['tots']['info']; Ia = I + r.get('senars', {}).get('info', []); mean = lambda f, I=I: float(np.mean([f(i) for i in I]))
        K2 = mean(lambda i: g(i['classes_K'], 2)); K32 = mean(lambda i: g(i['classes_K'], 32)); order = mean(lambda i: i['ordre'])
        tri = mean(lambda i: g(i['repetits'], 3)); five = mean(lambda i: g(i['repetits'], 5))
        C = {'C1 bateria': r['tots']['score'] >= 74 and r.get('senars', {}).get('score', 0) >= 70,
             "C2 forma de l'ordre": K2 <= 0.025 and 0.03 <= K32 <= 0.08, 'C3 ordre total': 0.06 <= order <= 0.12, 'C4 frases': tri <= 190 and five <= 2}
        res[var] = dict(r, criteris=C, K2=K2, K32=K32, ordre=order, trios=tri, cinc=five)
        lines.append(f"\n== {var.upper()} ({r['tots']['llavors']} llavors al text sencer, {r.get('senars', {}).get('llavors', 0)} a pàgines no vistes)")
        lines.append(f"  bateria: text sencer {r['tots']['score']}/88, pàgines no vistes {r.get('senars', {}).get('score', '-')}/88")
        lines.append(f"  falla (text sencer): {'; '.join(r['tots']['falla'])}")
        if 'senars' in r: lines.append(f"  falla (pàgines no vistes): {'; '.join(r['senars']['falla'])}")
        lines.append(f"  ordre {order:.3f} (llavors: {', '.join(f'{i['ordre']:.3f}' for i in I)}); classes " +
                     ' '.join(f"K={K}:{mean(lambda i, K=K: g(i['classes_K'], K)):.3f}" for K in (2, 4, 8, 16, 32)))
        lines.append('  repetits (seqüències diferents >= 2 cops) 2/3/4/5 mots: ' + ' / '.join(f"{mean(lambda i, n_=n_: g(i['repetits'], n_)):.0f}" for n_ in (2, 3, 4, 5)))
        lines.append(f"  capacitat {mean(lambda i: i['bits_per_mot']):.2f} bits/mot, {mean(lambda i: i['mots_llatins']):.0f} mots llatins; nul·les {100 * mean(lambda i: i['nulles']):.1f}%; "
                     f"intents/mot {mean(lambda i: i['intents'], Ia):.0f}; reserva {mean(lambda i: i['reserva'], Ia):.0f}; "
                     f"desxifrat {all(i['desxifrat_ok'] and i['llati_ok'] for i in Ia)}; tipus {mean(lambda i: i['tipus']):.0f} (real 7.915); "
                     f"repetició immediata {mean(lambda i: i['repeticio_immediata']):.4f} (real 0,0090)")
        lines.append('  criteris: ' + '; '.join(f"{k} {'SÍ' if v else 'NO'}" for k, v in C.items()))
    open(os.path.join(HERE, 'blanc.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n'); print('\n'.join(lines))
    json.dump(res, open(os.path.join(HERE, 'blanc.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'prova':
        var = sys.argv[2] if len(sys.argv) > 2 else 'b1'
        code, us, text = setup(); assert unwhiten(us) == text
        print('freqüències blanquejades:', sorted(Counter(us).values())[:3], '...', sorted(Counter(us).values())[-3:])
        lay = [l for l in SC.L_ALL if l['page'] in ('f1r', 'f75r', 'f103r')]
        g, nxt = make(var, code, us); t = time.time(); out = g.write(seed=1, layout=lay)
        n = sum(len(l['ws']) for l in out); dec = decode(code, out, nxt)
        print(f'{var}: {n} mots, {g.tries / n:.0f} intents/mot, {g.fb} de reserva, nul·les {getattr(g, "nulls", 0)}, {time.time() - t:.0f}s; '
              f'desxifrat == original: {dec == us[:g.pos]}; llatí: {unwhiten(dec)[:60]!r}')
        for l in out[:5]: print('  ', ' '.join(l['ws']))
    if mode == 'corre': run(sys.argv[2], sys.argv[3], int(sys.argv[4]))
    if mode == 'agrega': agrega()
