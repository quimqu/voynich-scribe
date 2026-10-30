# Laboratori de xifrats llatí -> voynichès (29/10/2026).
# Dades: el Voynich és el mateix de l'escriba (mesures.load_real: ZL3b, només paràgraf, comes unides, <-> = espai);
# el llatí és De docta ignorantia amb la maqueta de controls/llati.json.
# Mesures: (1) la corba d'entropia del notebook pm-cipher (word reset, dins mostra), (2) la mateixa amb espais i
# validació a pàgines no vistes (Witten-Bell), (3) la bateria de 76 mesures de l'escriba, (4) el pressupost d'informació.
import os, sys, math, json, random, re
from collections import Counter, defaultdict
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); NOV = os.environ.get('VOYNICH_NOV') or os.path.join(HERE, '_data')   # dades auxiliars (al repositori privat era la carpeta pare)
sys.path.insert(0, os.path.join(NOV, 'escriba'))
import mesures

GL = re.compile(r'cth|ckh|cph|cfh|ch|sh|[a-z]')


def voynich_lines(lang=None):
    L = mesures.load_real()
    return [l for l in L if lang is None or l['lang'] == lang]


def latin_lines():
    return json.load(open(os.path.join(NOV, 'escriba', 'controls', 'llati.json'), encoding='utf-8'))


def words(L):
    return [w for l in L for w in l['ws']]


def pour(L, ws):
    """Aboca una seqüència de mots a la maqueta real (mateixes línies, pàgines, paràgrafs i forats de dibuix)."""
    out = []; it = iter(ws)
    for l in L:
        new = []
        for _ in l['ws']:
            w = next(it, None)
            if w is None: break
            new.append(w)
        if not new: break
        out.append(dict(l, ws=new, gb=l['gb'][:len(new)]))
    return out


# ---------------------------------------------------------------- entropies
def h_wordreset(ws, n):
    """L'estimador del notebook (entropy_word_reset): H(x_n | n-1 anteriors) dins del mot, dins mostra, sense espais."""
    ctx = defaultdict(Counter)
    for w in ws:
        for i in range(len(w) - n + 1): ctx[w[i:i + n - 1]][w[i + n - 1]] += 1
    tot = 0; s = 0.0
    for c in ctx.values():
        m = sum(c.values()); tot += m
        s += -sum(v * math.log2(v / m) for v in c.values())
    return s / tot if tot else float('nan')


def curve_wordreset(ws, nmax=10):
    return [h_wordreset(ws, n) for n in range(1, nmax + 1)]


def _stream(L):
    return ['^' + ' '.join(l['ws']) + '$' for l in L]


def split_pages(L):
    pages = list(dict.fromkeys(l['page'] for l in L)); tr = set(pages[0::2])
    return [l for l in L if l['page'] in tr], [l for l in L if l['page'] not in tr]


class WB:
    """Model de caràcters amb interpolació Witten-Bell fins a l'ordre K (context de K-1 símbols)."""
    def __init__(self, seqs, K):
        self.K = K; self.c = [defaultdict(Counter) for _ in range(K)]
        self.V = len(set(ch for s in seqs for ch in s)) + 1
        for s in seqs:
            for i in range(1, len(s)):
                for k in range(K):
                    if i - k < 0: break
                    self.c[k][s[i - k:i]][s[i]] += 1

    def p(self, h, ch):
        pr = 1.0 / self.V
        for k in range(self.K):
            if len(h) < k: break
            cc = self.c[k].get(h[len(h) - k:] if k else '')
            if not cc: continue
            n = sum(cc.values()); t = len(cc)
            pr = (cc.get(ch, 0) + t * pr) / (n + t)
        return pr

    def xent(self, seqs):
        s = 0.0; n = 0
        for q in seqs:
            for i in range(1, len(q)):
                s -= math.log2(self.p(q[max(0, i - self.K + 1):i], q[i])); n += 1
        return s / n


def curve_heldout(L, kmax=8):
    tr, te = split_pages(L); a, b = _stream(tr), _stream(te)
    return [WB(a, k).xent(b) for k in range(1, kmax + 1)]


def bits_per_word(L, k=6):
    """Pressupost d'informació: bits per mot a pàgines no vistes (model de caràcters amb espais, ordre k)."""
    tr, te = split_pages(L); m = WB(_stream(tr), k); b = _stream(te)
    nch = sum(len(s) - 1 for s in b); nw = sum(len(l['ws']) for l in te)
    return m.xent(b) * nch / nw


def word_unigram_heldout(L):
    """Entropia creuada de mots (unigrama, mots nous via model de caràcters): una altra cota de capacitat per mot."""
    tr, te = split_pages(L); c = Counter(words(tr)); n = sum(c.values()); V = len(c)
    cm = WB(['^' + w + '$' for w in words(tr)], 5)
    def lp_char(w):
        s = '^' + w + '$'; return sum(-math.log2(cm.p(s[max(0, i - 4):i], s[i])) for i in range(1, len(s)))
    tot = 0.0; ws = words(te)
    for w in ws:
        pw = (c[w] + V * 2 ** -lp_char(w)) / (n + V)   # Witten-Bell a nivell de mot
        tot -= math.log2(pw)
    return tot / len(ws)


def battery(L, ref=None):
    R = mesures.evaluate(L)
    return {k: float(v) for k, v in R.items()}


def score(Rr, Rg, tol=0.25):
    ok = mesures.compare(Rr, Rg, tol)
    return sum(ok.values()), len(ok), ok
