# Xifrat «per model»: un model generatiu de voynichès (còpia de la pàgina + vocabulari de mà + contacte de frontera) fet servir
# com a xifrat. Els bits del llatí (lletres amb codi de Huffman) trien cada mot pel camí d'un arbre de Huffman construït
# sobre les probabilitats del model. Qui té el model desfà el camí i recupera els bits: es desxifra sense nota lateral.
# La capacitat (bits per mot) és exactament el que el model deixa triar. És la prova d'existència: qualsevol generador que
# s'assembli al Voynich es pot convertir en xifrat; la pregunta passa a ser quant llatí hi cap.
import math, heapq, re
from collections import Counter, defaultdict
GL = re.compile(r'cth|ckh|cph|cfh|ch|sh|[a-z]')


def huffman(weights):
    """{símbol: pes} -> {símbol: codi '0101'}"""
    if len(weights) == 1: return {next(iter(weights)): '0'}
    h = [(w, i, (s,)) for i, (s, w) in enumerate(weights.items())]; heapq.heapify(h); code = {s: '' for s in weights}; k = len(h)
    while len(h) > 1:
        w1, _, a = heapq.heappop(h); w2, _, b = heapq.heappop(h)
        for s in a: code[s] = '0' + code[s]
        for s in b: code[s] = '1' + code[s]
        heapq.heappush(h, (w1 + w2, k, a + b)); k += 1
    return code


def latin_bits(lat):
    """llatí -> bits (lletres i espai amb codi de Huffman per freqüència de lletra)"""
    s = ' '.join(lat); c = Counter(s); code = huffman(c)
    return ''.join(code[ch] for ch in s), code


class Model:
    def __init__(self, V, lam=0.22, window=40, beta=1.0, K=1024):
        self.lam, self.window, self.beta, self.K = lam, window, beta, K
        allw = [w for l in V for w in l['ws']]; self.glob = Counter(allw)
        self.byhand = defaultdict(Counter)
        for l in V: self.byhand[l['hand']].update(l['ws'])
        self.first = Counter(w[0] for w in allw); n = len(allw)
        self.pf = {k: v / n for k, v in self.first.items()}
        self.trans = defaultdict(Counter)
        for l in V:
            for a, b in zip(l['ws'], l['ws'][1:]): self.trans[a[-1]][b[0]] += 1
        self._nc = {}
        self.dv = defaultdict(set)          # variants per esborrat d'un glif: veïns a distància 1 (com mesures.delvars)
        for w in self.glob:
            g = GL.findall(w)
            for i in range(len(g)): self.dv[''.join(g[:i] + g[i + 1:])].add(w)
            self.dv[w].add(w)

    def neigh(self, w):
        if w in self._nc: return set(self._nc[w])
        g = GL.findall(w); out = set(self.dv.get(w, ()))
        for i in range(len(g)): out |= self.dv.get(''.join(g[:i] + g[i + 1:]), set())
        self._nc[w] = frozenset(out); return out

    def dist(self, hand, page_words, prev):
        fr = self.byhand.get(hand) or self.glob; tot = sum(fr.values()); gt = sum(self.glob.values())
        P = Counter()
        for w, v in fr.most_common(self.K): P[w] += (1 - self.lam) * (0.8 * v / tot + 0.2 * self.glob[w] / gt)
        rec = page_words[-self.window:]
        if rec:
            for s in rec:
                nb = self.neigh(s); nb.discard(s); P[s] += self.lam * 0.5 / len(rec)
                if nb:
                    z = sum(self.glob[x] for x in nb)
                    for x in nb: P[x] += self.lam * 0.5 / len(rec) * self.glob[x] / z
        if prev is not None and self.beta:
            t = self.trans[prev[-1]]; tt = sum(t.values()) or 1
            for w in P: P[w] *= ((t[w[0]] + 1) / tt / self.pf.get(w[0], 1e-4)) ** self.beta
        top = dict(P.most_common(self.K)); z = sum(top.values())
        return {w: p / z for w, p in top.items()}


def encode(V, lat, **kw):
    m = Model(V, **kw); bits, _ = latin_bits(lat); pos = 0; out = []; info = 0.0; used = 0
    pw = defaultdict(list)
    for l in V:
        page_words = pw[l['page']]
        ws = []; prev = None
        for _ in l['ws']:
            d = m.dist(l['hand'], page_words + ws, prev); code = huffman(d)
            inv = {c: w for w, c in code.items()}; cur = ''
            while cur not in inv:
                cur += bits[pos] if pos < len(bits) else '0'; pos += 1
            w = inv[cur]; ws.append(w); prev = w; used += len(cur); info += -math.log2(d[w])
        out.append(dict(l, ws=ws)); page_words.extend(ws)
    n = sum(len(o['ws']) for o in out)
    letters = bits[:min(pos, len(bits))]
    return out, dict(bits_per_word=used / n, model_bits_per_word=info / n, latin_bits_used=min(pos, len(bits)),
                     latin_bits_total=len(bits), latin_words_carried=round(len(lat) * min(pos, len(bits)) / len(bits)))


def decode(V, out, lat, **kw):
    """Comprova que es desxifra: refà els arbres i en recupera els bits."""
    m = Model(V, **kw); bits, code = latin_bits(lat); rec = []; pw = defaultdict(list)
    for l in out:
        page_words = pw[l['page']]
        prev = None; ws = []
        for w in l['ws']:
            d = m.dist(l['hand'], page_words + ws, prev); rec.append(huffman(d)[w]); ws.append(w); prev = w
        page_words.extend(ws)
    b = ''.join(rec); inv = {c: ch for ch, c in code.items()}; s = []; cur = ''
    for x in b:
        cur += x
        if cur in inv: s.append(inv[cur]); cur = ''
    return ''.join(s)


def logloss(V_train, V_test, eps=0.03, **kw):
    """Bits per mot del text real (pàgines no vistes) sota el model, amb el context real de la pàgina.
    És una cota superior de la informació que porta cada mot real si el text s'hagués fet amb aquest mecanisme."""
    import lab
    m = Model(V_train, **kw); cm = lab.WB(['^' + w + '$' for l in V_train for w in l['ws']], 5)
    def pchar(w):
        s = '^' + w + '$'; return 2 ** sum(math.log2(cm.p(s[max(0, i - 4):i], s[i])) for i in range(1, len(s)))
    pw = defaultdict(list); tot = 0.0; n = 0
    for l in V_test:
        page_words = pw[l['page']]; prev = None; ws = []
        for w in l['ws']:
            d = m.dist(l['hand'], page_words + ws, prev)
            tot -= math.log2((1 - eps) * d.get(w, 0.0) + eps * pchar(w)); n += 1; ws.append(w); prev = w
        page_words.extend(ws)
    return tot / n


# ---------------------------------------------------------------- versió amb maqueta: taules per mà i per posició a la línia
def slot(l, i):
    n = len(l['ws'])
    if i == 0: return 'P1' if l.get('ps') == 1 else 'L1'
    if i == n - 1: return 'LZ'
    return 'IF' if l.get('ps') == 1 else 'I'


class LayoutModel(Model):
    """Com Model, però el vocabulari de partida depèn de la mà i de la posició (primer mot de paràgraf, de línia, últim,
    interior de la primera línia de paràgraf, interior) i hi ha un pes extra per repetir el mot just anterior."""
    def __init__(self, V, aa=0.01, **kw):
        super().__init__(V, **kw); self.aa = aa
        self.tab = defaultdict(Counter)
        for l in V:
            for i, w in enumerate(l['ws']): self.tab[(l['hand'], slot(l, i))][w] += 1; self.tab[('*', slot(l, i))][w] += 1

    def dist(self, hand, page_words, prev, sl='I'):
        fr = self.tab.get((hand, sl)); fa = self.tab[('*', sl)]; fh = self.byhand.get(hand) or self.glob
        P = Counter(); ta = sum(fa.values()); th = sum(fh.values()); tf = sum(fr.values()) if fr else 0
        for src, wgt, tot in ((fr, 0.6, tf), (fa, 0.25, ta), (fh, 0.15, th)):
            if not src: continue
            for w, v in src.most_common(self.K): P[w] += (1 - self.lam - self.aa) * wgt * v / tot
        rec = page_words[-self.window:]
        if rec:
            for s in rec:
                nb = self.neigh(s); nb.discard(s); P[s] += self.lam * 0.5 / len(rec)
                if nb:
                    z = sum(self.glob[x] for x in nb)
                    for x in nb: P[x] += self.lam * 0.5 / len(rec) * self.glob[x] / z
        if prev is not None:
            P[prev] += self.aa
            if self.beta:
                t = self.trans[prev[-1]]; tt = sum(t.values()) or 1
                for w in P: P[w] *= ((t[w[0]] + 1) / tt / self.pf.get(w[0], 1e-4)) ** self.beta
        top = dict(P.most_common(self.K)); z = sum(top.values())
        return {w: p / z for w, p in top.items()}


def encode_layout(V, lat, layout=None, **kw):
    """V: text real d'on s'aprenen les taules; layout: maqueta que s'omple (per defecte, la mateixa V)."""
    m = LayoutModel(V, **kw); bits, _ = latin_bits(lat); pos = 0; out = []; used = 0; pw = defaultdict(list)
    for l in (layout or V):
        page_words = pw[l['page']]; ws = []; prev = None
        for i in range(len(l['ws'])):
            d = m.dist(l['hand'], page_words + ws, prev, slot(l, i)); code = huffman(d)
            inv = {c: w for w, c in code.items()}; cur = ''
            while cur not in inv:
                cur += bits[pos] if pos < len(bits) else '0'; pos += 1
            w = inv[cur]; ws.append(w); prev = w; used += len(cur)
        out.append(dict(l, ws=ws)); page_words.extend(ws)
    n = sum(len(o['ws']) for o in out)
    return out, dict(bits_per_word=used / n, latin_bits_used=min(pos, len(bits)), latin_bits_total=len(bits),
                     latin_words_carried=round(len(lat) * min(pos, len(bits)) / len(bits)),
                     key_entries=sum(len(c) for k, c in m.tab.items() if k[0] != '*'))


def decode_layout(V, out, lat, **kw):
    m = LayoutModel(V, **kw); bits, code = latin_bits(lat); rec = []; pw = defaultdict(list)
    for l in out:
        page_words = pw[l['page']]; prev = None; ws = []
        for i, w in enumerate(l['ws']):
            d = m.dist(l['hand'], page_words + ws, prev, slot(l, i)); rec.append(huffman(d)[w]); ws.append(w); prev = w
        page_words.extend(ws)
    b = ''.join(rec); inv = {c: ch for ch, c in code.items()}; s = []; cur = ''
    for x in b:
        cur += x
        if cur in inv: s.append(inv[cur]); cur = ''
    return ''.join(s)
