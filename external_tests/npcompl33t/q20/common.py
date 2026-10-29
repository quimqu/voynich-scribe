# Shared by the Q20 scripts: page scores of npcompl33t's ensemble (page_scores.json, from page_scores.py), the real Q20 lines,
# word log-odds models trained outside Q20, and the leave-one-sheet-out Q20 axis.
import os, sys, json, math, numpy as np
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'scribe'))
import measures as M
sys.stdout.reconfigure(encoding='utf-8')
S = json.load(open(os.path.join(HERE, 'page_scores.json'))); meta = S['_meta']
score = {p: S['real'][p] for p, (b, g) in meta.items() if b.startswith('T:')}   # 23 Q20 paragraph pages
bif = {p: meta[p][0] for p in score}
real = M.load_real()
lines = defaultdict(list)
for l in real:
    if l['page'] in score: lines[l['page']].append(l)
pages = sorted(score, key=score.get)
sheets = sorted(set(bif.values()), key=lambda b: np.mean([score[p] for p in score if bif[p] == b]))


def counts(sel): return Counter(w for l in real if sel(l) for w in l['ws'])


def logodds(cA, cB, a=0.5):
    V = set(cA) | set(cB); nA = sum(cA.values()); nB = sum(cB.values())
    return {w: math.log((cA[w] + a) / (nA + a * len(V))) - math.log((cB[w] + a) / (nB + a * len(V))) for w in V}


def pscore(ws, lo): v = [lo[w] for w in ws if w in lo]; return float(np.mean(v)) if v else np.nan


B_OUT = lambda l: l['lang'] == 'B' and l['quire'] != 'T'
herbal = lambda l: l['section'].lower().startswith('h')
LO = {   # trained without any Q20 line
    'Currier A-ness (vs B)': logodds(counts(lambda l: l['lang'] == 'A'), counts(B_OUT)),
    'Bio (Q13)-ness (vs other B)': logodds(counts(lambda l: l['quire'] == 'M'), counts(lambda l: B_OUT(l) and l['quire'] != 'M')),
    'Herbal B-ness (vs other B)': logodds(counts(lambda l: B_OUT(l) and herbal(l)), counts(lambda l: B_OUT(l) and not herbal(l))),
}


def loso(b):
    """Q20 axis for sheet b, learnt from the other five sheets only: words of the later half against the earlier half."""
    others = [s for s in sheets if s != b]; early, late = others[:len(others) // 2], others[len(others) // 2:]
    cE = Counter(w for p in score if bif[p] in early for l in lines[p] for w in l['ws'])
    cL = Counter(w for p in score if bif[p] in late for l in lines[p] for w in l['ws'])
    return logodds(cL, cE)


LOSO = {b: loso(b) for b in sheets}
