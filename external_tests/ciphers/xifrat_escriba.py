# El xifrat de dues capes (30/10/2026), fet amb l'skribe de voynich-scribe (98ecf31):
#  capa de xifrat: el text pla (lletres i espai) es talla en unitats; cada unitat és una classe de mots. La classe d'un mot es
#    llegeix de la seva forma normalitzada (sense la capa d'escrivà: tancament de final de línia -m/-ly/-ry/-sy/-g desfet,
#    p/f -> k/t, sense q-), amb una taula repartida per massa sobre el vocabulari real (allocate); formes noves, per una regla fixa.
#  capa d'escrivà: l'skribe sencer (còpia, contacte, hàbits de mà i de full, registres de línia, tancaments). A cada mot, l'skribe
#    fa la seva tria com sempre i només s'accepta si cau a la classe de la unitat que toca (si no, torna a triar). La sortida és,
#    doncs, l'skribe condicionat al missatge: es desxifra mot a mot amb la taula, sense cap nota a part.
#   py -3 xifrat_escriba.py prova    -> roundtrip en unes pàgines
#   py -3 xifrat_escriba.py corre    -> xifrat_escriba.json (bateria, holdout, ordre dels mots, capacitat)
import os, sys, re, math, json, random, zlib, inspect, textwrap, time
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); SCRIBE = (os.environ.get('SCRIBE') or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'scribe'))
sys.path.insert(0, SCRIBE); sys.path.insert(0, HERE)
if len(sys.argv) > 2 and sys.argv[2] == 'senars': os.environ['SCRIBE_TRAIN'] = 'odd'
os.chdir(SCRIBE)
import scribe as SC
os.chdir(HERE)
import lab, ciphers

END = [('iin', 'N'), ('in', 'N'), ('m', 'N'), ('ly', 'l'), ('ry', 'r'), ('sy', 's'), ('g', 'y')]


def norm(w):
    """la forma sense la capa d'escrivà"""
    w = w.replace('cph', 'ckh').replace('cfh', 'cth').replace('p', 'k').replace('f', 't')
    if w.startswith('q') and len(w) > 1: w = w[1:]
    while True:   # fins que no canvia: -y tancada en -g sobre un -ly (oly -> olg) ha de tornar a ol
        for o, n in END:
            if w.endswith(o) and len(w) >= len(o) and w != n: w2 = w[:-len(o)] + n; break
        else: return w
        if w2 == w: return w
        w = w2


class Code:
    def __init__(self, units_freq, real_words):
        kf = Counter(norm(w) for w in real_words)
        table, missing = ciphers.allocate(units_freq, kf)
        self.missing = missing
        self.cls = {k: u for u, ks in table.items() for k, _ in ks}
        self.units = sorted(units_freq); self.words = {}
        for w, c in Counter(real_words).items(): self.words.setdefault(self.of(w), Counter())[w] += c

    def of(self, w):
        k = norm(w)
        return self.cls.get(k) or self.units[zlib.crc32(k.encode()) % len(self.units)]


def units_of(text, p_bigram=0.0, seed=5, allowed=None):
    r = random.Random(seed); out = []; i = 0
    while i < len(text):
        L = 2 if (p_bigram and r.random() < p_bigram and i + 1 < len(text) and (allowed is None or text[i:i + 2] in allowed)) else 1
        out.append(text[i:i + L]); i += L
    return out


# ---------------- l'skribe amb la tria condicionada: es reescriu write() posant un bucle de reintents al voltant de cada mot
def _patched_write():
    src = textwrap.dedent(inspect.getsource(SC.Escriba.write)).split('\n')
    i0 = next(i for i, s in enumerate(src) if s.strip() == "for i in range(len(l['ws'])):")
    i1 = next(i for i, s in enumerate(src) if s.strip().startswith("ws.append(w); page_words.append((w,li,i))"))
    ind = ' ' * (len(src[i0 + 1]) - len(src[i0 + 1].lstrip()))
    body = ['    ' + s if s.strip() else s for s in src[i0 + 1:i1]]
    new = src[:i0 + 1] + [ind + 'for _t in range(self.max_tries):'] + body + \
          [ind + '    if self.accept(w, page_words): break', ind + 'else:', ind + '    w=self.fallback()'] + src[i1:]
    ns = dict(SC.__dict__); exec('\n'.join(new), ns); return ns['write']


class Cipher(SC.Escriba):
    write = _patched_write()

    def __init__(self, code, units, max_tries=400, **kw):
        super().__init__(**kw); self.code, self.units, self.max_tries = code, units, max_tries; self.pos = 0; self.fb = 0; self.tries = 0

    def _target(self):
        return self.units[self.pos] if self.pos < len(self.units) else self.units[-1]

    def accept(self, w, page_words=None):
        self.tries += 1
        if self.code.of(w) == self._target(): self.pos += 1; return True
        return False

    def fallback(self):
        c = self.code.words.get(self._target()); self.fb += 1; self.pos += 1
        return self.rng.choices(list(c), weights=list(c.values()))[0]


def decode(code, L):
    return [code.of(w) for l in L for w in l['ws']]


def setup(p_bigram=0.0):
    real = [l for l in SC.L_ALL]; lat = lab.words(lab.latin_lines()); text = ' '.join(lat)
    rw = [w for l in real for w in l['ws']]; us = units_of(text, p_bigram); code = Code(Counter(us), rw)
    while code.missing:   # els parells de lletres massa rars per tenir cap forma pròpia es tornen dues unitats d'una lletra
        allowed = set(us) - set(code.missing); us = units_of(text, p_bigram, allowed=allowed); code = Code(Counter(us), rw)
    return code, us, text


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'prova'
    if mode == 'prova':
        code, us, text = setup()
        lay = [l for l in SC.L_ALL if l['page'] in ('f1r', 'f1v', 'f2r', 'f75r', 'f103r')]
        c = Cipher(code, us); t = time.time(); out = c.write(seed=1, layout=lay)
        n = sum(len(l['ws']) for l in out); dec = ''.join(decode(code, out))
        print(f'{n} mots, {c.tries / n:.1f} intents/mot, {c.fb} de reserva, {time.time() - t:.0f}s')
        print('desxifrat == original:', dec == text[:len(dec)], repr(dec[:120]))
        for l in out[:6]: print('  ', ' '.join(l['ws']))

    if mode == 'corre':
        # py -3 xifrat_escriba.py corre <tots|senars> <skribe|1|12> <llavor>  -> xe/<tots|senars>_<variant>_<llavor>.json
        # (per poder córrer cada llavor en un procés; agrega.py en fa la mitjana i la comparació)
        import numpy as np
        sys.path.insert(0, os.path.join(lab.NOV, 'escriba', 'controls')); import control
        M = SC.M; split, var, seed = sys.argv[2], sys.argv[3], int(sys.argv[4])
        hand = {l['page']: l['hand'] for l in SC.L_ALL}
        lay = [l for l in SC.L_ALL if SC.folio_num(l['page']) % 2 == 0] if split == 'senars' else None
        if var == 'skribe': g = SC.Escriba(); H = 0.0; lpw = 0.0; text = ''
        else:
            code, us, text = setup(0.0 if var == '1' else 0.5)
            g = Cipher(code, us, max_tries=400 if var == '1' else 3000)
            H = -sum(v / len(us) * math.log2(v / len(us)) for v in Counter(us).values()); lpw = len(text) / len(us)
        t = time.time(); out = g.write(seed=seed, layout=lay)
        for o in out: o['hand'] = hand[o['page']]
        r = M.evaluate(out, seed=seed); n = sum(len(o['ws']) for o in out)
        ok = None
        if var != 'skribe' and split == 'tots': ok = X_ok = (decode(code, out) == us[:g.pos])
        info = dict(ordre=control.word_order(out), intents=getattr(g, 'tries', n) / n, reserva=getattr(g, 'fb', 0), unitats=getattr(g, 'pos', 0),
                    segons=time.time() - t, bits_per_mot=H, lletres_per_mot=lpw, mots=n, desxifrat_ok=ok,
                    mots_llatins=(getattr(g, 'pos', 0) * lpw / (len(text) / len(text.split()))) if text else 0)
        os.makedirs(os.path.join(HERE, 'xe'), exist_ok=True)
        json.dump(dict(R={k: float(v) for k, v in r.items()}, info=info), open(os.path.join(HERE, 'xe', f'{split}_{var}_{seed}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
        print(split, var, seed, info, flush=True)
