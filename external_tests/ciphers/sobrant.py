# Hi ha informació al Voynich que l'skribe no explica? (29/10/2026)
# Mateix estimador per a tots els textos: el model s'aprèn de les pàgines de foli senar i es mesura el cost (bits per mot)
# de les de foli parell. Si el text real costa clarament més que el text de l'skribe, hi ha una sorpresa per mot que cap
# hàbit d'escriptura de l'skribe no fa: és on podria viure un missatge. Si costen igual, no queda lloc per a res més.
#   py -3 sobrant.py    -> sobrant.json, sobrant_taula.txt
import os, sys, json, math, re
from collections import Counter
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIBE = (os.environ.get('SCRIBE') or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'scribe'))
sys.path.insert(0, SCRIBE); sys.path.insert(0, HERE)
os.chdir(SCRIBE)
from scribe import Escriba, L_ALL, folio_num
os.chdir(HERE)
import lab, stego

hand = {l['page']: l['hand'] for l in L_ALL}
def norm(L):
    return [dict(l, hand=l.get('hand', hand.get(l['page'], '?')), locus=l.get('locus', l['page'])) for l in L]
def halves(L):
    return [l for l in L if folio_num(l['page']) % 2 == 1], [l for l in L if folio_num(l['page']) % 2 == 0]

def scores(L):
    tr, te = halves(L); nw = sum(len(l['ws']) for l in te)
    a, b = lab._stream(tr), lab._stream(te); nch = sum(len(s) - 1 for s in b)
    car = min(lab.WB(a, k).xent(b) for k in (3, 4, 5)) * nch / nw
    # mots: unigrama Witten-Bell amb model de caràcters per als mots nous
    c = Counter(w for l in tr for w in l['ws']); n = sum(c.values()); V = len(c)
    cm = lab.WB(['^' + w + '$' for l in tr for w in l['ws']], 5)
    def pc(w):
        s = '^' + w + '$'; return 2 ** sum(math.log2(cm.p(s[max(0, i - 4):i], s[i])) for i in range(1, len(s)))
    ws = [w for l in te for w in l['ws']]
    uni = -sum(math.log2((c[w] + V * pc(w)) / (n + V)) for w in ws) / len(ws)
    oov = 100 * sum(1 for w in ws if w not in c) / len(ws)
    ctx = stego.logloss(tr, te)
    return dict(caracters=car, unigrama=uni, context=ctx, mots_nous=oov, tipus=len(set(ws)))

def cross(train, test):
    """el model après d'un text, mesurat sobre un altre (pàgines parelles)"""
    tr, _ = halves(train); _, te = halves(test)
    return stego.logloss(tr, te)

if __name__ == '__main__':
    R = {}
    real = norm(L_ALL); R['real'] = scores(real); print('real', R['real'], flush=True)
    sk = []
    for s in (1, 2, 3):
        S = norm(Escriba().write(seed=s)); sk.append(S)
        R[f'skribe {s}'] = scores(S); print(f'skribe {s}', R[f'skribe {s}'], flush=True)
    os.environ['SCRIBE_TRAIN'] = 'odd'
    # control: skribe après només dels senars (no ha vist les pàgines parelles que es mesuren)
    import importlib, scribe as _sc
    os.chdir(SCRIBE); importlib.reload(_sc); os.chdir(HERE)
    S = norm(_sc.Escriba().write(seed=1)); R['skribe après dels senars'] = scores(S); print('skribe senars', R['skribe après dels senars'], flush=True)
    # creuat: el model de context après de l'skribe, mesurat sobre el real i sobre un altre skribe
    R['creuat: model de l\'skribe sobre el real'] = cross(sk[0], real)
    R['creuat: model de l\'skribe sobre un altre skribe'] = cross(sk[0], sk[1])
    R['creuat: model del real sobre l\'skribe'] = cross(real, sk[1])
    print({k: v for k, v in R.items() if k.startswith('creuat')})
    json.dump(R, open(os.path.join(HERE, 'sobrant.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
