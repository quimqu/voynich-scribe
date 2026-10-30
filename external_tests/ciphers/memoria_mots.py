# La prova que decideix §7.4 de XIFRATS.md (30/10/2026): l'skribe amb una memòria de mot a mot i SENSE missatge.
# Hàbit: parelles de mots que s'atreuen (mot A seguit de mot B a la mateixa línia més sovint del que tocaria), apreses NOMÉS dels
# folis senars del real; sense parelles iguals ni a un glif (això ja és la còpia de l'skribe). Mentre escriu, a cada mot que no és
# el primer de la línia, amb probabilitat lam l'skribe «segueix l'hàbit»: torna a triar fins que el mot fa parella atreta amb
# l'anterior (com a molt 200 intents; si no en troba cap, es queda l'últim). La resta del procediment no es toca.
# Es mesura als folis PARELLS (parelles no vistes): informació d'ordre (ordre.py) i la seva forma, amb l'agrupament de classes
# de classes.py (après dels senars del mateix text, mesurat als parells). Si omple l'ordre amb la forma del real (res a K=2,
# ~0,05 a K>=16), el forat era un hàbit de l'escrivà; si no, un codi de molts símbols passa a ser el millor candidat.
# La força de l'hàbit (lam) es calibra perquè l'ordre dels mots arribi al del real (0,088); el que es prova és la FORMA.
#   py -3 memoria_mots.py real                              -> mm/real.json
#   py -3 memoria_mots.py corre <lam> <llavor> <estreta|ampla> -> mm/<taula>_<lam>_<llavor>.json (lam 0 = skribe sol; ~5 min)
#   (SCRIBE = carpeta scribe de voynich-scribe, si no és a C:\dev-quimqu\ o C:\dev\)
import os, sys, json, math, random, inspect, textwrap, time
from collections import Counter, defaultdict
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIBE = (os.environ.get('SCRIBE') or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'scribe'))
sys.path.insert(0, SCRIBE); os.chdir(SCRIBE)
import scribe as SC
os.chdir(HERE); sys.stdout.reconfigure(encoding='utf-8')
src = open(os.path.join(HERE, 'classes.py'), encoding='utf-8').read()
exec(src[src.index('def pairs('):src.index("if __name__")])          # pairs, mi, exchange, heldout de classes.py, tal qual
OUT = os.path.join(HERE, 'mm'); os.makedirs(OUT, exist_ok=True)
odd_ = lambda L: [l for l in L if SC.folio_num(l['page']) % 2]; even_ = lambda L: [l for l in L if not SC.folio_num(l['page']) % 2]


def near(a, b): return a == b or SC.M.lev(a, b) <= 1


def attraction(L, min_pair=3, min_pmi=1.0):
    """parelles A -> B de la mateixa línia, comptades >= min_pair vegades i amb PMI >= min_pmi bits, sense iguals ni a un glif"""
    P = Counter(pairs(L)); n = sum(P.values()); a_ = Counter(a for a, _ in P.elements()); b_ = Counter(b for _, b in P.elements())
    nxt = defaultdict(set)
    for (a, b), c in P.items():
        if c >= min_pair and not near(a, b) and math.log2(c * n / (a_[a] * b_[b])) >= min_pmi: nxt[a].add(b)
    return nxt


def order(L, K=200, reps=5):   # ordre.py / control.word_order: MI entre mots seguits menys la dels mots barrejats dins la línia
    top = set(w for w, _ in Counter(w for l in L for w in l['ws']).most_common(K)); m = lambda w: w if w in top else '*'
    real = mi([(m(a), m(b)) for l in L for a, b in zip(l['ws'], l['ws'][1:])]); rng = random.Random(0); base = []
    for _ in range(reps):
        pp = []
        for l in L:
            ws = l['ws'][:]; rng.shuffle(ws); pp += [(m(a), m(b)) for a, b in zip(ws, ws[1:])]
        base.append(mi(pp))
    return real - float(np.mean(base))


def _patched_write():   # com xifrat_escriba.py, però accept() rep la línia que s'està escrivint (ws) per saber el mot anterior
    s = textwrap.dedent(inspect.getsource(SC.Escriba.write)).split('\n')
    i0 = next(i for i, x in enumerate(s) if x.strip() == "for i in range(len(l['ws'])):")
    i1 = next(i for i, x in enumerate(s) if x.strip().startswith("ws.append(w); page_words.append((w,li,i))"))
    ind = ' ' * (len(s[i0 + 1]) - len(s[i0 + 1].lstrip()))
    body = ['    ' + x if x.strip() else x for x in s[i0 + 1:i1]]
    new = s[:i0 + 1] + [ind + 'self._start(ws)', ind + 'for _t in range(self.max_tries):'] + body + \
          [ind + '    if self.accept(w): break'] + s[i1:]
    ns = dict(SC.__dict__); exec('\n'.join(new), ns); return ns['write']


class Memoria(SC.Escriba):
    write = _patched_write()

    def __init__(self, nxt, lam, max_tries=200, **kw):
        super().__init__(**kw); self.nxt, self.lam, self.max_tries = nxt, lam, max_tries; self.tries = self.follow = self.hit = 0

    def _start(self, ws):   # abans de cada mot: hi ha mot anterior a la línia amb parelles apreses, i l'escrivà segueix l'hàbit?
        self.want = None
        if ws and ws[-1] in self.nxt and self.rng.random() < self.lam: self.want = self.nxt[ws[-1]]; self.follow += 1

    def accept(self, w):
        self.tries += 1
        if self.want is None: return True
        if w in self.want: self.hit += 1; return True
        return False


TABLES = {'estreta': (3, 1.0), 'ampla': (2, 0.5)}   # parelles vistes >= 3 cops amb PMI >= 1 bit (162), o >= 2 cops amb PMI >= 0,5 (627)


def run(lam, seed, table):
    real = SC.L_ALL; nxt = attraction(odd_(real), *TABLES[table]); hand = {l['page']: l['hand'] for l in real}
    g = SC.Escriba() if lam == 0 else Memoria(nxt, lam)
    t = time.time(); out = g.write(seed=seed); n = sum(len(l['ws']) for l in out)
    for o in out: o['hand'] = hand[o['page']]
    B = SC.M.evaluate(out, seed=seed); ok = SC.M.compare(SC.M.evaluate(real, seed=1), B)   # bateria de 88, com agrega.py
    r = dict(lam=lam, seed=seed, taula=table, segons=time.time() - t, mots=n, parelles_apreses=sum(len(v) for v in nxt.values()),
             segueix=getattr(g, 'follow', 0) / n, encerta=getattr(g, 'hit', 0) / max(1, getattr(g, 'follow', 0)),
             ordre_tot=order(out), ordre_senars=order(odd_(out)), ordre_parells=order(even_(out)),
             tipus=len(set(w for l in out for w in l['ws'])), bateria=int(sum(ok.values())), falla=[k for k, v in ok.items() if not v],
             classes={K: heldout(exchange(odd_(out), K), even_(out)) for K in (2, 4, 8, 16, 32)})
    nm = 'skribe' if lam == 0 else f'{table}_{lam}'
    json.dump(r, open(os.path.join(OUT, f'{nm}_{seed}.json'), 'w'), indent=1); print(r, flush=True)


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'corre': run(float(sys.argv[2]), int(sys.argv[3]), sys.argv[4] if len(sys.argv) > 4 else 'estreta')
    if mode == 'real':
        real = SC.L_ALL
        r = dict(ordre_tot=order(real), ordre_senars=order(odd_(real)), ordre_parells=order(even_(real)), tipus=len(set(w for l in real for w in l['ws'])),
                 classes={K: heldout(exchange(odd_(real), K), even_(real)) for K in (2, 4, 8, 16, 32)})
        json.dump(r, open(os.path.join(OUT, 'real.json'), 'w'), indent=1); print(r, flush=True)
