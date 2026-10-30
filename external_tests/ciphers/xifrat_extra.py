# Proves de més sobre el xifrat de dues capes (30/10/2026):
#  nul·les  — un mot igual a un mot ja escrit a la pàgina (forma normalitzada) és nul (amb «a un glif» ho eren el 97%): no porta res i el lector se'l
#             salta. Així la còpia de l'skribe queda lliure i només els mots «nous» porten el missatge.
#  llengua  — el mateix xifrat amb llatí, vietnamita (VIQR), xinès (pinyin) i un missatge de lletres a l'atzar: les estadístiques
#             del text xifrat veuen quina llengua hi ha a sota?
#  sobrant  — el text xifrat costa més bits per mot que l'skribe sol (la prova de §5)? I on (freqüència dels mots)?
#  desxifrat — el manuscrit sencer es desxifra exacte.
#   py -3 xifrat_extra.py <prova> [senars]   prova = nulles | llengua | sobrant | desxifrat
import os, sys, re, json, math, random, time
from collections import Counter
import numpy as np
mode = sys.argv[1]
import xifrat_escriba as X
SC = X.SC; M = SC.M
import lab
HERE = X.HERE
GLN = re.compile(r'cth|ckh|cph|cfh|ch|sh|[a-zN]')
hand = {l['page']: l['hand'] for l in SC.L_ALL}


def dv(k):
    g = GLN.findall(k); return {''.join(g[:i] + g[i + 1:]) for i in range(len(g))} | {k}


class NullCipher(X.Cipher):
    """els mots que repeteixen (o varien en un glif) un mot ja escrit a la pàgina són nuls"""
    def accept(self, w, page_words=None):
        self.tries += 1
        k = X.norm(w); prev = {X.norm(pw) for pw, _, _ in (page_words or [])}
        self._pv = prev
        if k in prev:
            # una repetició sempre és nul·la; si se n'acceptessin totes, el text s'ompliria de repeticions (83% contra 34% real).
            # Racionades (null_p): s'accepten amb la probabilitat d'encertar una classe, i la sortida queda com la de l'skribe
            if self.null_p >= 1 or self.rng.random() < self.null_p: self.nulls += 1; return True
            return False       # nul: no gasta unitat
        if self.code.of(w) == self._target(): self.pos += 1; return True
        return False

    def __init__(self, *a, **kw):
        self.null_p = kw.pop('null_p', 1.0); super().__init__(*a, **kw); self.nulls = 0; self._pv = set()

    def fallback(self):
        # la paraula de reserva no pot semblar un nul
        c = {w: v for w, v in self.code.words.get(self._target(), {}).items() if X.norm(w) not in self._pv}
        self.fb += 1; self.pos += 1
        return self.rng.choices(list(c), weights=list(c.values()))[0]


def decode_nulls(code, L):
    out = []; page = None
    for l in L:
        if l['page'] != page: page = l['page']; pv = set()
        for w in l['ws']:
            k = X.norm(w)
            if k not in pv: out.append(code.of(w))
            pv.add(k)
    return out


def text_of(name):
    if name == 'llatí': return ' '.join(lab.words(lab.latin_lines()))
    raw = open(os.path.join(lab.NOV, 'vietnamese.txt' if name == 'vietnamita' else 'chinese.txt'), encoding='utf-8', errors='ignore').read().lower()
    toks = [t for t in re.split(r'[^a-z0-9]+', raw.replace("'", '').replace('`', '').replace('^', '').replace('+', '')) if t]
    return ' '.join(toks)


def setup_text(text, p_bigram=0.0):
    rw = [w for l in SC.L_ALL for w in l['ws']]; us = X.units_of(text, p_bigram); code = X.Code(Counter(us), rw)
    while code.missing:
        allowed = set(us) - set(code.missing); us = X.units_of(text, p_bigram, allowed=allowed); code = X.Code(Counter(us), rw)
    return code, us


def evaluate(out, s):
    for o in out: o['hand'] = hand[o['page']]
    return M.evaluate(out, seed=s)


if __name__ == '__main__':
    sys.path.insert(0, os.path.join(lab.NOV, 'escriba', 'controls')); import control
    odd = len(sys.argv) > 2 and sys.argv[2] == 'senars'
    lay = [l for l in SC.L_ALL if SC.folio_num(l['page']) % 2 == 0] if odd else None
    ref = M.evaluate(lay if odd else SC.L_ALL, seed=1); R = {}
    tag = mode + ('_senars' if odd else '')
    if mode in ('nulles', 'nulles2'):
        text = text_of('llatí')
        for pb, nm in ((0.0, '1 lletra'), (0.5, '1-2 lletres')):
            np_ = 1.0
            if mode == 'nulles2':
                # probabilitat que una proposta de l'skribe encerti la classe que toca: les classes tenen la massa de la unitat, sum p^2
                cu = Counter(X.units_of(text, pb)); np_ = sum(v * v for v in cu.values()) / sum(cu.values()) ** 2
            code, us = setup_text(text, pb); H = -sum(v / len(us) * math.log2(v / len(us)) for v in Counter(us).values())
            sc = []; inf = []
            for s in (1, 2, 3):
                c = NullCipher(code, us, null_p=np_); out = c.write(seed=s, layout=lay); r = evaluate(out, s); sc.append(r)
                n = sum(len(o['ws']) for o in out)
                inf.append(dict(nuls=c.nulls / n, intents=c.tries / n, reserva=c.fb, unitats=c.pos, ordre=control.word_order(out)))
                if s == 1:
                    dec = ''.join(decode_nulls(code, out)); inf[-1]['desxifrat_ok'] = dec == ''.join(us[:c.pos])
            G = {k: float(np.mean([r[k] for r in sc])) for k in sc[0]}; ok = M.compare(ref, G)
            units = np.mean([x['unitats'] for x in inf]); nw = sum(len(l['ws']) for l in (lay or SC.L_ALL))
            R[nm] = dict(score=sum(ok.values()), n=len(ok), null_p=np_, fails=[k for k, v in ok.items() if not v], info=inf,
                         bits_per_mot=H * units / nw, mots_llatins=units * (len(text) / len(us)) / (len(text) / len(text.split())))
            print('nul·les', nm, R[nm]['score'], '/', len(ok), {k: v for k, v in R[nm].items() if k not in ('fails', 'info')}, inf[0], flush=True)
    if mode == 'llengua':
        rng = random.Random(9); lat = text_of('llatí'); f = Counter(lat)
        texts = {'llatí': lat, 'vietnamita': text_of('vietnamita'), 'xinès (pinyin)': text_of('xinès'),
                 'lletres a l\'atzar (freq. del llatí)': ''.join(rng.choices(list(f), weights=list(f.values()), k=len(lat))),
                 'lletres a l\'atzar (uniformes)': ''.join(rng.choice('abcdefghilmnopqrstuvx ') for _ in range(len(lat)))}
        for nm, t in texts.items():
            code, us = setup_text(t); sc = []; od = []
            for s in (1, 2, 3):
                out = X.Cipher(code, us).write(seed=s, layout=lay); sc.append(evaluate(out, s)); od.append(control.word_order(out))
            G = {k: float(np.mean([r[k] for r in sc])) for k in sc[0]}; ok = M.compare(ref, G)
            R[nm] = dict(score=sum(ok.values()), n=len(ok), ordre=float(np.mean(od)), fails=[k for k, v in ok.items() if not v], G=G)
            print('llengua', nm, R[nm]['score'], '/', len(ok), 'ordre', R[nm]['ordre'], flush=True)
    if mode == 'sobrant':
        import sobrant
        code, us, text = X.setup(0.0); code2, us2, _ = X.setup(0.5)
        for s in (1, 2, 3):
            for nm, g in (('skribe', lambda: SC.Escriba()), ('xifrat 1 lletra', lambda: X.Cipher(code, us)), ('xifrat 1-2 lletres', lambda: X.Cipher(code2, us2))):
                out = g().write(seed=s)
                for o in out: o['hand'] = hand[o['page']]; o['locus'] = o['page']
                L = sobrant.norm(out); R[f'{nm} {s}'] = sobrant.scores(L); print(nm, s, R[f'{nm} {s}'], flush=True)
    if mode == 'desxifrat':
        for pb in (0.0, 0.5):
            code, us, text = X.setup(pb); c = X.Cipher(code, us); out = c.write(seed=4)
            dec = X.decode(code, out); R[str(pb)] = dict(ok=dec == us[:len(dec)], unitats=len(dec), reserva=c.fb,
                                                         lletres=len(''.join(dec)), inici=''.join(dec)[:300])
            print('desxifrat', pb, R[str(pb)], flush=True)
    json.dump(R, open(os.path.join(HERE, f'xifrat_extra_{tag}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
